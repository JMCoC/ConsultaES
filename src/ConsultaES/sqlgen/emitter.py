from consultaES.semantics.ast import SQLAst, Column, Condition, Join


def emit(ast: SQLAst) -> tuple[str, list]:
    """Convierte un SQLAst a (cadena_sql, parametros) usando consultas parametrizadas."""
    parts = []
    params = []

    # SELECT
    select_cols = [_col_to_str(col) for col in ast.select]
    parts.append("SELECT " + ", ".join(select_cols))

    # FROM + JOINs
    if ast.joins:
        from_str = "FROM " + ast.tables[0]
        for j in ast.joins:
            from_str += (
                f" JOIN {j.table}"
                f" ON {_col_to_str(j.on_left)} = {_col_to_str(j.on_right)}"
            )
        parts.append(from_str)
    else:
        parts.append("FROM " + ", ".join(ast.tables))

    # WHERE
    if ast.where:
        where_parts = []
        for connector, cond in ast.where:
            cond_str, cond_params = _cond_to_str(cond)
            if connector:
                where_parts.append(f"{connector} {cond_str}")
            else:
                where_parts.append(cond_str)
            params.extend(cond_params)
        parts.append("WHERE " + " ".join(where_parts))

    # GROUP BY
    if ast.group_by:
        parts.append("GROUP BY " + ", ".join(_col_to_str(c) for c in ast.group_by))

    # HAVING
    if ast.having:
        having_parts = []
        for connector, cond in ast.having:
            cond_str, cond_params = _cond_to_str(cond)
            if connector:
                having_parts.append(f"{connector} {cond_str}")
            else:
                having_parts.append(cond_str)
            params.extend(cond_params)
        parts.append("HAVING " + " ".join(having_parts))

    # ORDER BY
    if ast.order_by:
        ob_parts = [f"{_col_to_str(col)} {direction}" for col, direction in ast.order_by]
        parts.append("ORDER BY " + ", ".join(ob_parts))

    # LIMIT
    if ast.limit is not None:
        parts.append(f"LIMIT {ast.limit}")

    return " ".join(parts), params


def _col_to_str(col: Column) -> str:
    base = f"{col.table}.{col.name}" if col.table else col.name
    if col.agg:
        return f"{col.agg}({base})"
    return base


def _cond_to_str(cond: Condition) -> tuple[str, list]:
    col_str = _col_to_str(cond.col)
    if cond.op == "BETWEEN" and isinstance(cond.value, (list, tuple)) and len(cond.value) == 2:
        neg = "NOT " if cond.negated else ""
        return f"{col_str} {neg}BETWEEN ? AND ?", list(cond.value)
    if cond.op == "IN" and isinstance(cond.value, (list, tuple)):
        placeholders = ", ".join("?" for _ in cond.value)
        neg = "NOT " if cond.negated else ""
        return f"{col_str} {neg}IN ({placeholders})", list(cond.value)
    neg = "NOT " if cond.negated else ""
    return f"{neg}{col_str} {cond.op} ?", [cond.value]
