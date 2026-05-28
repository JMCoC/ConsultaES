"""DCG attribute evaluation — walks a ParseTree bottom-up and produces a SQLAst."""

from __future__ import annotations

from consultaES.lexicon import LexicalItem
from consultaES.parser.tree import ParseTree
from consultaES.semantics.ast import Column, Condition, SQLAst



_OP_MAP: dict[str, str] = {
    "igual a": "=",
    "mayor que": ">",
    "menor que": "<",
    "mayor o igual a": ">=",
    "menor o igual a": "<=",
    "diferente de": "!=",
    "=": "=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "!=": "!=",
}


_AGG_MAP: dict[str, str] = {
    "total": "SUM",
    "suma": "SUM",
    "promedio": "AVG",
    "media": "AVG",
    "cuenta": "COUNT",
    "cantidad": "COUNT",
    "máximo": "MAX",
    "mínimo": "MIN",
}


def _normalize_op(lemma: str) -> str:
    low = lemma.strip().lower()
    if low in _OP_MAP:
        return _OP_MAP[low]
    return low


def _to_number(s: str):
    """Intenta convertir a int, luego float; devuelve str si falla."""
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def _strip_quotes(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s



def _eval_leaf(item: LexicalItem) -> dict:
    cat = item.category
    lemma = item.lemma
    bindings = item.bindings

    if cat == "N_TABLA":
        return {"tipo": "tabla", "tabla": lemma}
    if cat == "N_COLUMNA":
        return {"tipo": "columna", "columna": lemma, "bindings": bindings}
    if cat in ("INTERROG", "IMPERATIVO"):
        modo = "interrog" if cat == "INTERROG" else "imperativo"
        return {"tipo": "modo", "modo": modo}
    if cat == "NUM":
        return {"tipo": "valor", "valor": _to_number(lemma)}
    if cat == "CADENA":
        return {"tipo": "valor", "valor": _strip_quotes(lemma)}
    if cat in ("VALOR_CIUDAD", "VALOR_NOMBRE", "VALOR_CATEGORIA", "VALOR_TIPO"):
        return {"tipo": "valor", "valor": lemma, "bindings": bindings}
    if cat == "OP_COMP":
        return {"tipo": "op", "op": _normalize_op(lemma)}
    if cat == "DET":
        return {"tipo": "det"}
    if cat == "PREP":
        return {"tipo": "prep", "prep": lemma}
    if cat == "CONECTOR":
        conector = "AND" if lemma.lower() == "y" else "OR"
        return {"tipo": "conector", "conector": conector}
    if cat == "AGG":
        sql_agg = _AGG_MAP.get(lemma.lower(), "COUNT")
        return {"tipo": "agg", "agg": sql_agg}
    if cat == "AGR_MARKER":
        return {"tipo": "agr_marker"}
    if cat == "ORD_MARKER":
        return {"tipo": "ord_marker"}
    if cat == "DIR":
        low = lemma.lower()
        direction = "DESC" if low.startswith("descend") else "ASC"
        return {"tipo": "dir", "dir": direction}

    # Fallback
    return {"tipo": cat.lower(), "lemma": lemma}



def _eval_node(label: str, child_attrs: list[dict], children) -> dict | SQLAst:
    """Aplica la acción semántica de una regla interna.

    ``children`` es la lista original de hijos (ParseTree | LexicalItem) para
    poder inspeccionar sus etiquetas / categorías si es necesario.
    """
    rhs_labels = tuple(
        c.label if isinstance(c, ParseTree) else c.category for c in children
    )

    # ----- S -> Pregunta -----
    if label == "S":
        return child_attrs[0]

    # ----- Pregunta -----
    if label == "Pregunta":
        # Pregunta -> Nucleo | Nucleo Cola
        nucleo_ast = child_attrs[0] 
        if len(child_attrs) == 2:
            cola = child_attrs[1]  
            if cola.get("filtros"):
                filtros = list(cola["filtros"])
                if nucleo_ast.where and filtros and filtros[0][0] == "":
                    filtros[0] = ("AND", filtros[0][1])
                nucleo_ast.where = nucleo_ast.where + filtros
            if cola.get("agrupacion"):
                nucleo_ast.group_by = [
                    Column(table=None, name=cola["agrupacion"]["columna"])
                ]
            if cola.get("orden"):
                orden = cola["orden"]
                direction = orden.get("dir", "ASC")
                nucleo_ast.order_by = [
                    (Column(table=None, name=orden["columna"]), direction)
                ]
        return nucleo_ast

    # ----- Nucleo -----
    if label == "Nucleo":
        agg_attr = None
        sn_attr = None
        valor_attr = None

        for ca in child_attrs:
            if isinstance(ca, dict):
                tipo = ca.get("tipo")
                if tipo == "agregacion":
                    agg_attr = ca
                elif tipo == "tabla":
                    sn_attr = ca
                elif tipo == "valor":
                    valor_attr = ca
                elif tipo in ("modo", "prep", "det"):
                    pass

        if sn_attr is None:
            raise ValueError("Nucleo sin SN (tabla)")

        tabla = sn_attr["tabla"]

        if agg_attr:
            agg_func = agg_attr["agg"]
            agg_col = agg_attr.get("columna")
            if agg_col:
                select = [Column(table=tabla, name=agg_col, agg=agg_func)]
            else:
                select = [Column(table=tabla, name="*", agg=agg_func)]
        else:
            select = [Column(table=tabla, name="*")]

        ast = SQLAst(select=select, tables=[tabla])

        if rhs_labels == ("SN", "PREP", "Valor") and valor_attr:
            bindings = valor_attr.get("bindings") or []
            if bindings:
                table, column = bindings[0]
                ast.where = [
                    (
                        "",
                        Condition(
                            col=Column(table=table, name=column),
                            op="=",
                            value=valor_attr.get("valor"),
                        ),
                    )
                ]

        # LIMIT from SN
        if sn_attr.get("limit") is not None:
            ast.limit = sn_attr["limit"]

        return ast

    # ----- Cola -----
    if label == "Cola":
        result: dict = {}
        for ca in child_attrs:
            if isinstance(ca, dict):
                tipo = ca.get("tipo")
                if tipo == "agrupacion":
                    result["agrupacion"] = ca
                elif tipo == "orden":
                    result["orden"] = ca
            elif isinstance(ca, list):
                result["filtros"] = ca
        return result

    # ----- Interrog / Imperativo -----
    if label in ("Interrog", "Imperativo"):
        return child_attrs[0]

    # ----- SN -----
    if label == "SN":
        if len(child_attrs) == 1:
            # SN -> N_TABLA
            return child_attrs[0]
        if len(child_attrs) == 2:
            # SN -> Det N_TABLA
            return child_attrs[1]
        if len(child_attrs) == 3:
            # SN -> Det NUM N_TABLA
            tabla_attr = child_attrs[2]
            num_attr = child_attrs[1]
            limit_val = num_attr.get("valor")
            if isinstance(limit_val, (int, float)):
                tabla_attr["limit"] = int(limit_val)
            return tabla_attr

    # ----- Det -----
    if label == "Det":
        return child_attrs[0]

    # ----- Filtros -----
    if label == "Filtros":
        filtro_cond = child_attrs[0]  # Condition
        if len(child_attrs) == 1:
            return [("", filtro_cond)]
        # Filtros -> Filtro CONECTOR Filtros
        conector_attr = child_attrs[1]
        rest = child_attrs[2]  # list of (conector, cond)
        result = [("", filtro_cond)]
        for _, cond in rest:
            result.append((conector_attr["conector"], cond))
        return result

    # ----- Filtro -> PREP N_COLUMNA OP_COMP Valor -----
    if label == "Filtro":
        col_attr = child_attrs[1]
        op_attr = child_attrs[2]
        val_attr = child_attrs[3]
        valor = val_attr.get("valor", val_attr.get("lemma"))
        return Condition(
            col=Column(table=None, name=col_attr["columna"]),
            op=op_attr["op"],
            value=valor,
        )

    # ----- Agregacion -----
    if label == "Agregacion":
        agg_attr = child_attrs[0]  # AGG leaf
        result = {"tipo": "agregacion", "agg": agg_attr["agg"]}
        if len(child_attrs) == 3:
            # Agregacion -> AGG PREP N_COLUMNA
            col_attr = child_attrs[2]
            result["columna"] = col_attr["columna"]
        return result

    # ----- Agrupacion -----
    if label == "Agrupacion":
        # Agrupacion -> AGR_MARKER PREP N_COLUMNA
        col_attr = child_attrs[2]
        return {"tipo": "agrupacion", "columna": col_attr["columna"]}

    # ----- Orden -----
    if label == "Orden":
        # Orden -> ORD_MARKER PREP N_COLUMNA [Direccion]
        col_attr = child_attrs[2]
        result = {"tipo": "orden", "columna": col_attr["columna"]}
        if len(child_attrs) == 4:
            dir_attr = child_attrs[3]
            result["dir"] = dir_attr["dir"]
        return result

    # ----- Direccion -----
    if label == "Direccion":
        return child_attrs[0]

    # ----- Valor -----
    if label == "Valor":
        return child_attrs[0]

    # Fallback — no debería ocurrir con la gramática actual
    return child_attrs[0] if child_attrs else {}


def interpret(tree: ParseTree) -> SQLAst:
    """Recorre el ParseTree en post-orden y produce un SQLAst."""
    result = _walk(tree)
    if not isinstance(result, SQLAst):
        raise ValueError(f"El nodo raíz no produjo un SQLAst: {result!r}")
    return result


def _walk(node):
    """Recorrido post-orden: evalúa hijos, luego aplica la acción del nodo."""
    if isinstance(node, LexicalItem):
        return _eval_leaf(node)

    child_attrs = [_walk(c) for c in node.children]
    return _eval_node(node.label, child_attrs, node.children)
