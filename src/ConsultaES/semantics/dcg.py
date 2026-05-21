
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


def _normalize_op(lemma: str) -> str:
    low = lemma.strip().lower()
    if low in _OP_MAP:
        return _OP_MAP[low]
    return low


def _to_number(s: str):
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
    if cat == "VALOR_CIUDAD":
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

    return {"tipo": cat.lower(), "lemma": lemma}


def _eval_node(label: str, child_attrs: list[dict], children) -> dict | SQLAst:
    rhs_labels = tuple(
        c.label if isinstance(c, ParseTree) else c.category for c in children
    )

    if label == "S":
        return child_attrs[0]


    if label == "Pregunta":
        sn = child_attrs[1]
        tabla = sn["tabla"]
        ast = SQLAst(
            select=[Column(table=tabla, name="*")],
            tables=[tabla],
        )
        if len(child_attrs) >= 3:
            filtros = child_attrs[2]
            ast.where = filtros
        return ast

    if label in ("Interrog", "Imperativo"):
        return child_attrs[0]

    if label == "SN":
        if len(child_attrs) == 1:
            return child_attrs[0]
        return child_attrs[1]

    if label == "Det":
        return child_attrs[0]

    if label == "Filtros":
        filtro_cond = child_attrs[0] 
        if len(child_attrs) == 1:
            return [("", filtro_cond)]
        conector_attr = child_attrs[1]
        rest = child_attrs[2]  
        result = [("", filtro_cond)]
        for _, cond in rest:
            result.append((conector_attr["conector"], cond))
        return result

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

    if label == "Valor":
        return child_attrs[0]

    return child_attrs[0] if child_attrs else {}


def interpret(tree: ParseTree) -> SQLAst:
    result = _walk(tree)
    if not isinstance(result, SQLAst):
        raise ValueError(f"El nodo raíz no produjo un SQLAst: {result!r}")
    return result


def _walk(node):
    if isinstance(node, LexicalItem):
        return _eval_leaf(node)

    child_attrs = [_walk(c) for c in node.children]
    return _eval_node(node.label, child_attrs, node.children)
