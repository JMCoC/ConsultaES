from __future__ import annotations

import sqlite3
from typing import Iterable

from consultaES.lexicon import LexicalItem, Lexicon
from consultaES.parser.tree import ParseTree


_VALUE_CATEGORIES = {"VALOR_NOMBRE", "VALOR_CIUDAD", "VALOR_CATEGORIA", "VALOR_TIPO"}

_NUMERIC_COL_NAMES = {"id", "total", "precio", "cantidad", "precio_unitario"}
_NUMERIC_COL_PREFIXES = ("id_",)
_DATE_COL_PREFIXES = ("fecha",)


def _iter_leaves(node) -> Iterable[LexicalItem]:
    if isinstance(node, LexicalItem):
        yield node
        return
    if isinstance(node, ParseTree):
        for c in node.children:
            yield from _iter_leaves(c)


def _iter_subtrees(node) -> Iterable[ParseTree]:
    if isinstance(node, ParseTree):
        yield node
        for c in node.children:
            yield from _iter_subtrees(c)


def _column_sql_type(table: str, col: str, lex: Lexicon) -> str:
    low = (col or "").lower()
    if low in _NUMERIC_COL_NAMES or low.startswith(_NUMERIC_COL_PREFIXES):
        return "numeric"
    if low.startswith(_DATE_COL_PREFIXES):
        return "date"
    return "text"


def _value_kind(v) -> str:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return "numeric"
    if isinstance(v, str):
        try:
            float(v)
            return "numeric"
        except (TypeError, ValueError):
            return "text"
    return "text"


def _rule_schema_existence(tree: ParseTree, lex: Lexicon) -> int:
    try:
        for leaf in _iter_leaves(tree):
            if not leaf.bindings:
                continue
            ok = False
            for (t, c) in leaf.bindings:
                if t not in lex.tables:
                    continue
                if c is None or c in lex.tables[t]:
                    ok = True
                    break
            if not ok:
                return 0
        return 3
    except Exception:
        return 0

_NUMERIC_OPS = {">", "<", ">=", "<=", "BETWEEN"}


def _filtro_subtrees(tree: ParseTree) -> list[ParseTree]:
    return [n for n in _iter_subtrees(tree) if n.label == "Filtro"]


def _rule_type_compat(tree: ParseTree, lex: Lexicon) -> int:
    try:
        filtros = _filtro_subtrees(tree)
        if not filtros:
            return 0  
        for filtro in filtros:
            col_leaf = None
            op_leaf = None
            val_node = None
            for ch in filtro.children:
                if isinstance(ch, LexicalItem):
                    if ch.category == "N_COLUMNA":
                        col_leaf = ch
                    elif ch.category == "OP_COMP":
                        op_leaf = ch
                elif isinstance(ch, ParseTree) and ch.label == "Valor":
                    val_node = ch
            if col_leaf is None or val_node is None:
                continue  
            col_name = col_leaf.lemma
            col_table = None
            if col_leaf.bindings:
                col_table = col_leaf.bindings[0][0]
            col_type = _column_sql_type(col_table or "", col_name, lex)

            val_leaf = next(iter(_iter_leaves(val_node)), None)
            if val_leaf is None:
                continue
            if val_leaf.category == "NUM":
                val_type = "numeric"
            elif val_leaf.category in _VALUE_CATEGORIES or val_leaf.category == "CADENA":
                val_type = "text"
            elif val_leaf.category == "FECHA":
                val_type = "date"
            else:
                val_type = _value_kind(val_leaf.lemma)

            op_lemma = (op_leaf.lemma.strip().lower() if op_leaf else "=")
            op_norm = {
                "mayor que": ">",
                "menor que": "<",
                "mayor o igual a": ">=",
                "menor o igual a": "<=",
                "diferente de": "!=",
                "igual a": "=",
            }.get(op_lemma, op_lemma)

            if op_norm in _NUMERIC_OPS:
                if col_type != "numeric" or val_type != "numeric":
                    return 0
            elif op_norm in ("=", "!="):
                if col_type == "numeric" and val_type != "numeric":
                    return 0
                if col_type == "text" and val_type == "numeric":
                    return 0
        return 2
    except Exception:
        return 0

def _max_depth_of_label(node, label: str, depth: int = 0) -> int:
    found = -1
    if isinstance(node, ParseTree):
        if node.label == label:
            found = depth
        for c in node.children:
            sub = _max_depth_of_label(c, label, depth + 1)
            if sub > found:
                found = sub
    return found


def _rightmost_position(node, label: str) -> tuple[int, ...] | None:
    best: tuple[int, ...] | None = None

    def _walk(n, path: tuple[int, ...]) -> None:
        nonlocal best
        if isinstance(n, ParseTree):
            if n.label == label:
                if best is None or path > best:
                    best = path
            for i, c in enumerate(n.children):
                _walk(c, path + (i,))

    _walk(node, ())
    return best


def _rule_right_attachment(tree: ParseTree) -> int:
    try:
        pp_pos = _rightmost_position(tree, "Filtros")
        if pp_pos is None:
            pp_pos = _rightmost_position(tree, "SP")
        if pp_pos is None:
            return 0
        sn_pos = _rightmost_position(tree, "SN")
        if sn_pos is None:
            return 0
        return 1 if pp_pos > sn_pos else 0
    except Exception:
        return 0

def _rule_value_frequency(
    tree: ParseTree, lex: Lexicon, db_path: str | None
) -> int:
    try:
        contributions = 0
        for filtro in _filtro_subtrees(tree):
            val_node = next(
                (c for c in filtro.children if isinstance(c, ParseTree) and c.label == "Valor"),
                None,
            )
            if val_node is None:
                continue
            val_leaf = next(iter(_iter_leaves(val_node)), None)
            if val_leaf is None or val_leaf.category not in _VALUE_CATEGORIES:
                continue
            if not val_leaf.bindings:
                continue
            (t, c) = val_leaf.bindings[0]
            if db_path is not None:
                count = _count_value_in_db(db_path, t, c, val_leaf.lemma)
            else:
                vset = lex.values_by_table.get((t, c), set())
                count = 5 if (val_leaf.lemma in vset and len(vset) >= 5) else 0
            if count >= 5:
                contributions = 1
                break  
        return contributions
    except Exception:
        return 0


def _count_value_in_db(db_path: str, table: str, column: str, value) -> int:
    try:
        con = sqlite3.connect(db_path)
        try:
            cur = con.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (value,)
            )
            (n,) = cur.fetchone()
            return int(n)
        finally:
            con.close()
    except Exception:
        return 0


def _rule_zero_rows(tree: ParseTree, lex: Lexicon, db_path: str | None) -> int:
    if db_path is None:
        return 0
    try:
        from consultaES.semantics import interpret, resolve_joins
        from consultaES.sqlgen import generate

        ast = interpret(tree)
        ast = resolve_joins(ast, lex)
        sql, _ = generate(ast, db=None, execute=False)
        wrapped = f"SELECT 1 FROM ({sql}) AS _sub LIMIT 1"
        from consultaES.sqlgen.emitter import emit
        _sql, params = emit(ast)
        con = sqlite3.connect(db_path)
        try:
            cur = con.execute(wrapped, params)
            row = cur.fetchone()
            return -2 if row is None else 0
        finally:
            con.close()
    except Exception:
        return 0

def _rule_result_support(tree: ParseTree, lex: Lexicon, db_path: str | None) -> int:
    """+2 si la lectura genera una cantidad recurrente de filas reales.

    Extiende la señal de ejecución usada por la regla de 0 filas: una rama
    no solo debe ser no vacía, sino tener respaldo claro en el dominio. Esto
    permite resolver ambigüedades como ``ventas de Carlos`` cuando una lectura
    está mucho más respaldada por pedidos reales y la otra queda como caso
    escaso. El umbral evita romper empates genuinos que deben ir a Capa 3.
    """
    if db_path is None:
        return 0
    try:
        row_count = _count_result_rows(tree, lex, db_path)
        return 2 if row_count >= 8 else 0
    except Exception:
        return 0


def _count_result_rows(tree: ParseTree, lex: Lexicon, db_path: str) -> int:
    from consultaES.semantics import interpret, resolve_joins
    from consultaES.sqlgen.emitter import emit

    ast = resolve_joins(interpret(tree), lex)
    sql, params = emit(ast)
    wrapped = f"SELECT COUNT(*) FROM ({sql}) AS _sub"
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(wrapped, params)
        (count,) = cur.fetchone()
        return int(count)
    finally:
        con.close()

def score(
    tree: ParseTree,
    ctx,
    lex: Lexicon,
    db_path: str | None = None,
) -> int:
    """Suma ponderada de las cinco reglas heurísticas.

    Mayor puntaje = árbol preferido. Cualquier regla que no pueda
    evaluarse contribuye 0 (nunca lanza excepción).
    """
    total = 0
    total += _rule_schema_existence(tree, lex)
    total += _rule_type_compat(tree, lex)
    total += _rule_right_attachment(tree)
    total += _rule_value_frequency(tree, lex, db_path)
    total += _rule_zero_rows(tree, lex, db_path)
    total += _rule_result_support(tree, lex, db_path)
    return total


__all__ = ["score"]
