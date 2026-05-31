import sqlite3
from consultaES.errors import Error
from consultaES.semantics.ast import SQLAst
from .emitter import emit


def generate(ast: SQLAst, db=None, execute: bool = True) -> tuple[str, list]:
    sql, params = emit(ast)
    if not execute or db is None:
        return sql, []
    if isinstance(db, str):
        con = sqlite3.connect(db)
        try:
            cur = con.execute(sql, params)
            rows = cur.fetchall()
            return sql, rows
        finally:
            con.close()
    cur = db.execute(sql, params)
    return sql, cur.fetchall()


def generate_or_error(ast: SQLAst, db=None, execute: bool = True) -> tuple[str, list] | Error:
    sql = ""
    try:
        sql, rows = generate(ast, db=db, execute=execute)
        return sql, rows
    except sqlite3.Error as exc:
        if not sql:
            sql, _params = emit(ast)
        return Error(
            kind="ejecución",
            pos=None,
            message=f"Error SQLite al ejecutar SQL: {sql}. Detalle: {exc}",
            suggestions=[sql],
        )
