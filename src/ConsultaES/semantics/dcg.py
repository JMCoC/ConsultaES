from __future__ import annotations

from consultaES.lexicon import LexicalItem
from consultaES.errors import Error
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


_MONTHS = {
    "enero": "01",
    "febrero": "02",
    "marzo": "03",
    "abril": "04",
    "mayo": "05",
    "junio": "06",
    "julio": "07",
    "agosto": "08",
    "septiembre": "09",
    "octubre": "10",
    "noviembre": "11",
    "diciembre": "12",
}

_MONTH_DAYS = {
    "01": "31",
    "02": "28",
    "03": "31",
    "04": "30",
    "05": "31",
    "06": "30",
    "07": "31",
    "08": "31",
    "09": "30",
    "10": "31",
    "11": "30",
    "12": "31",
}

_TEMPORAL_COLUMNS = {
    "pedidos": "fecha",
    "clientes": "fecha_registro",
    "vendedores": "fecha_ingreso",
}


def _agg_column_from_select(ast: SQLAst, agg: str) -> tuple[str | None, str]:
    for col in ast.select:
        if col.agg == agg and col.name:
            return col.table, col.name
    return None, "*"


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


def _like_pattern(marker: str, value: object) -> str:
    text = str(value)
    low = marker.strip().lower()
    if low == "empieza con":
        return f"{text}%"
    if low == "termina con":
        return f"%{text}"
    return f"%{text}%"


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _month_days(month: str, year: str) -> int:
    if month == "02" and _is_leap_year(int(year)):
        return 29
    return int(_MONTH_DAYS[month])


def _normalize_fecha(texto: str) -> tuple[str, str]:
    low = texto.strip().lower()
    if low.isdigit() and len(low) == 4:
        return f"{low}-01-01", f"{low}-12-31"
    if low in _MONTHS:
        month = _MONTHS[low]
        return f"2025-{month}-01", f"2025-{month}-{_MONTH_DAYS[month]}"
    parts = low.split()
    if len(parts) == 3 and parts[1] == "de":
        if parts[0] in _MONTHS:
            month = _MONTHS[parts[0]]
            year = parts[2]
            if year.isdigit() and len(year) == 4:
                return f"{year}-{month}-01", f"{year}-{month}-{_month_days(month, year):02d}"
        if parts[0].isdigit() and parts[2] in _MONTHS:
            day = int(parts[0])
            month = _MONTHS[parts[2]]
            if 1 <= day <= int(_MONTH_DAYS[month]):
                iso = f"2025-{month}-{day:02d}"
                return iso, iso
            raise ValueError(f"Fecha no soportada: {texto}")
    if len(parts) == 5 and parts[1] == "de" and parts[3] == "de":
        if parts[0].isdigit() and parts[2] in _MONTHS and parts[4].isdigit():
            day = int(parts[0])
            month = _MONTHS[parts[2]]
            year = parts[4]
            if len(year) != 4 or day < 1 or day > _month_days(month, year):
                raise ValueError(f"Fecha no soportada: {texto}")
            iso = f"{year}-{month}-{day:02d}"
            return iso, iso
    raise ValueError(f"Fecha no soportada: {texto}")


def _temporal_column_for(tabla: str) -> str:
    if tabla not in _TEMPORAL_COLUMNS:
        raise ValueError(f"La tabla {tabla} no tiene columna temporal canónica")
    return _TEMPORAL_COLUMNS[tabla]


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
    if cat == "FECHA":
        return {"tipo": "fecha", "valor": lemma}
    if cat == "OP_LIKE":
        return {"tipo": "op_like", "op": "LIKE", "marker": lemma}
    if cat == "RANGO":
        return {"tipo": "rango"}
    if cat == "NEG":
        return {"tipo": "neg"}

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
            if cola.get("having"):
                nucleo_ast.having = cola["having"]
                for _, cond in nucleo_ast.having:
                    if cond.col.name == "*" and cond.col.agg != "COUNT":
                        table, name = _agg_column_from_select(nucleo_ast, cond.col.agg)
                        cond.col.table = table
                        cond.col.name = name
        return nucleo_ast

    # ----- Nucleo -----
    if label == "Nucleo":
        # Find SN (tabla) and optional Agregacion among children
        agg_attr = None
        sn_attr = None
        valor_attr = None
        proyeccion_attr = None

        for ca in child_attrs:
            if isinstance(ca, dict):
                tipo = ca.get("tipo")
                if tipo == "agregacion":
                    agg_attr = ca
                elif tipo == "tabla":
                    sn_attr = ca
                elif tipo in ("valor", "fecha"):
                    valor_attr = ca
                elif tipo == "proyeccion":
                    proyeccion_attr = ca
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
            if proyeccion_attr:
                select = [
                    Column(table=tabla, name=columna)
                    for columna in proyeccion_attr["columnas"]
                ]
            else:
                select = [Column(table=tabla, name="*")]
        ast = SQLAst(select=select, tables=[tabla])

        if rhs_labels == ("SN", "PREP", "Valor") and valor_attr:
            if valor_attr.get("tipo") == "fecha":
                lo, hi = _normalize_fecha(valor_attr["valor"])
                ast.where = [
                    (
                        "",
                        Condition(
                            col=Column(table=tabla, name=_temporal_column_for(tabla)),
                            op="BETWEEN",
                            value=(lo, hi),
                        ),
                    )
                ]
            else:
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
        result: dict = {"filtros": [], "having": []}
        for ca in child_attrs:
            if isinstance(ca, list):
                result["filtros"].extend(ca)
            elif isinstance(ca, dict):
                tipo = ca.get("tipo")
                if tipo == "agrupacion":
                    result["agrupacion"] = ca
                elif tipo == "orden":
                    result["orden"] = ca
                elif tipo == "having":
                    result["having"].extend(ca["having"])
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

    if label == "Filtro":
        if rhs_labels == ("NEG", "Filtro"):
            cond = child_attrs[1]
            cond.negated = True
            return cond

        col_attr = child_attrs[1]
        col = Column(table=None, name=col_attr["columna"])

        if rhs_labels == ("PREP", "N_COLUMNA", "OP_COMP", "Valor"):
            op_attr = child_attrs[2]
            val_attr = child_attrs[3]
            valor = val_attr.get("valor", val_attr.get("lemma"))
            return Condition(col=col, op=op_attr["op"], value=valor)

        if rhs_labels == ("PREP", "N_COLUMNA", "OP_LIKE", "Valor"):
            op_attr = child_attrs[2]
            val_attr = child_attrs[3]
            valor = val_attr.get("valor", val_attr.get("lemma"))
            return Condition(
                col=col,
                op="LIKE",
                value=_like_pattern(op_attr["marker"], valor),
            )

        if rhs_labels == ("PREP", "N_COLUMNA", "RANGO", "Valor", "CONECTOR", "Valor"):
            left = child_attrs[3].get("valor", child_attrs[3].get("lemma"))
            right = child_attrs[5].get("valor", child_attrs[5].get("lemma"))
            return Condition(col=col, op="BETWEEN", value=(left, right))

        if rhs_labels == ("PREP", "N_COLUMNA", "PREP", "ListaValores"):
            return Condition(col=col, op="IN", value=child_attrs[3])

        raise ValueError(f"Forma de filtro no soportada: {rhs_labels}")
    if label == "Proyeccion":
        first = child_attrs[0]["columna"]
        if len(child_attrs) == 1:
            return {"tipo": "proyeccion", "columnas": [first]}
        return {"tipo": "proyeccion", "columnas": [first] + child_attrs[2]["columnas"]}

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

    if label == "Having":
        agg_attr = child_attrs[1]
        op_attr = child_attrs[2]
        val_attr = child_attrs[3]
        value = val_attr.get("valor", val_attr.get("lemma"))
        agg = agg_attr["agg"]
        name = "*"
        if agg != "COUNT":
            for ca in child_attrs:
                if isinstance(ca, dict) and ca.get("tipo") == "columna":
                    name = ca["columna"]
        return {
            "tipo": "having",
            "having": [
                (
                    "",
                    Condition(
                        col=Column(table=None, name=name, agg=agg),
                        op=op_attr["op"],
                        value=value,
                    ),
                )
            ],
        }

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

    if label == "ListaValores":
        first = child_attrs[0].get("valor", child_attrs[0].get("lemma"))
        if len(child_attrs) == 1:
            return [first]
        return [first] + child_attrs[2]

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


def interpret_or_error(tree: ParseTree) -> SQLAst | Error:
    try:
        return interpret(tree)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return Error(
            kind="semántico",
            pos=0,
            message=f"No se pudo construir el SQLAst por incompatibilidad semántica: {exc}",
            suggestions=["Revisa la tabla, columna o valor usado en la consulta."],
        )


def _walk(node):
    """Recorrido post-orden: evalúa hijos, luego aplica la acción del nodo."""
    if isinstance(node, LexicalItem):
        return _eval_leaf(node)

    child_attrs = [_walk(c) for c in node.children]
    return _eval_node(node.label, child_attrs, node.children)
