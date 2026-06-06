import sqlite3
from consultaES.errors import Error
from consultaES.semantics.ast import SQLAst
from .emitter import emit


def generate(
    ast: SQLAst,
    db=None,
    execute: bool = True,
    include_columns: bool = False,
) -> tuple[str, list] | tuple[str, list, list[str]]:
    sql, params = emit(ast)
    if not execute or db is None:
        if include_columns:
            return sql, [], []
        return sql, []
    if isinstance(db, str):
        con = sqlite3.connect(db)
        try:
            cur = con.execute(sql, params)
            rows = cur.fetchall()
            columns = _column_names(cur)
            if include_columns:
                return sql, rows, columns
            return sql, rows
        finally:
            con.close()
    cur = db.execute(sql, params)
    rows = cur.fetchall()
    if include_columns:
        return sql, rows, _column_names(cur)
    return sql, rows


def generate_or_error(
    ast: SQLAst,
    db=None,
    execute: bool = True,
    include_columns: bool = False,
) -> tuple[str, list] | tuple[str, list, list[str]] | Error:
    sql = ""
    try:
        return generate(ast, db=db, execute=execute, include_columns=include_columns)
    except sqlite3.Error as exc:
        if not sql:
            sql, _params = emit(ast)
        return Error(
            kind="ejecución",
            pos=None,
            message=f"Error SQLite al ejecutar SQL: {sql}. Detalle: {exc}",
            suggestions=[sql],
        )


def _column_names(cur) -> list[str]:
    if cur.description is None:
        return []
    return [column[0] for column in cur.description]
