import sqlite3
from consultaES.semantics.ast import SQLAst
from .emitter import emit


def generate(ast: SQLAst, db=None, execute: bool = True) -> tuple[str, list]:
    sql, params = emit(ast)
    if not execute or db is None:
        return sql, []
    if isinstance(db, str):
        con = sqlite3.connect(db)
        cur = con.execute(sql, params)
        rows = cur.fetchall()
        con.close()
        return sql, rows
    cur = db.execute(sql, params)
    return sql, cur.fetchall()
