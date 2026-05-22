import pytest
from consultaES.semantics.ast import SQLAst, Column, Condition
from consultaES.sqlgen import generate
from consultaES.sqlgen.emitter import emit


def norm(s):
    return " ".join(s.lower().split())


def test_simple_select():
    ast = SQLAst(select=[Column("clientes", "*")], tables=["clientes"])
    sql, _ = generate(ast, db=None, execute=False)
    assert norm(sql) == "select clientes.* from clientes"


def test_select_sin_tabla():
    """Columna sin tabla calificada."""
    ast = SQLAst(select=[Column(None, "*")], tables=["clientes"])
    sql, _ = generate(ast, db=None, execute=False)
    assert norm(sql) == "select * from clientes"


def test_select_with_where():
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[("", Condition(Column(None, "ciudad"), "=", "Cali"))],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert norm(sql) == "select clientes.* from clientes where ciudad = ?"


def test_where_with_and():
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[
            ("", Condition(Column(None, "ciudad"), "=", "Cali")),
            ("AND", Condition(Column(None, "tipo"), "=", "premium")),
        ],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert norm(sql) == "select clientes.* from clientes where ciudad = ? and tipo = ?"


def test_aggregation():
    ast = SQLAst(
        select=[Column("pedidos", "total", agg="SUM")],
        tables=["pedidos"],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert norm(sql) == "select sum(pedidos.total) from pedidos"


def test_group_by():
    ast = SQLAst(
        select=[Column("clientes", "ciudad"), Column("clientes", "*", agg="COUNT")],
        tables=["clientes"],
        group_by=[Column("clientes", "ciudad")],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert "group by" in norm(sql)
    assert "clientes.ciudad" in norm(sql)


def test_order_by():
    ast = SQLAst(
        select=[Column("productos", "*")],
        tables=["productos"],
        order_by=[(Column("productos", "precio"), "DESC")],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert "order by" in norm(sql)
    assert "desc" in norm(sql)


def test_limit():
    ast = SQLAst(
        select=[Column("productos", "*")],
        tables=["productos"],
        limit=5,
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert "limit 5" in norm(sql)


def test_params_returned():
    """emit() devuelve los parametros correctos para WHERE."""
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[("", Condition(Column(None, "ciudad"), "=", "Cali"))],
    )
    _, params = emit(ast)
    assert params == ["Cali"]


def test_params_multiples():
    """emit() devuelve parametros para multiples condiciones WHERE."""
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[
            ("", Condition(Column(None, "ciudad"), "=", "Cali")),
            ("AND", Condition(Column(None, "tipo"), "=", "premium")),
        ],
    )
    _, params = emit(ast)
    assert params == ["Cali", "premium"]


def test_between():
    """BETWEEN genera dos placeholders."""
    ast = SQLAst(
        select=[Column("pedidos", "*")],
        tables=["pedidos"],
        where=[("", Condition(Column(None, "total"), "BETWEEN", [100, 500]))],
    )
    sql, params = emit(ast)
    assert "between ? and ?" in norm(sql)
    assert params == [100, 500]


def test_in_operator():
    """IN genera placeholders separados por coma."""
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[("", Condition(Column(None, "ciudad"), "IN", ["Cali", "Bogota", "Medellin"]))],
    )
    sql, params = emit(ast)
    assert "in (?, ?, ?)" in norm(sql)
    assert params == ["Cali", "Bogota", "Medellin"]


def test_negated_condition():
    """Condicion negada incluye NOT."""
    ast = SQLAst(
        select=[Column("clientes", "*")],
        tables=["clientes"],
        where=[("", Condition(Column(None, "ciudad"), "=", "Cali", negated=True))],
    )
    sql, _ = emit(ast)
    assert "NOT" in sql


def test_having():
    """HAVING se emite correctamente."""
    ast = SQLAst(
        select=[Column("clientes", "ciudad"), Column("clientes", "id", agg="COUNT")],
        tables=["clientes"],
        group_by=[Column("clientes", "ciudad")],
        having=[("", Condition(Column("clientes", "id", agg="COUNT"), ">", 3))],
    )
    sql, params = emit(ast)
    assert "HAVING" in sql
    assert params == [3]


def test_multiples_tablas():
    """FROM con dos tablas."""
    ast = SQLAst(
        select=[Column("pedidos", "id"), Column("clientes", "nombre")],
        tables=["pedidos", "clientes"],
    )
    sql, _ = generate(ast, db=None, execute=False)
    assert "pedidos, clientes" in sql


def test_execute_against_db():
    """Ejecuta contra la BD real de prueba."""
    ast = SQLAst(
        select=[Column(None, "*")],
        tables=["clientes"],
        where=[("", Condition(Column(None, "ciudad"), "=", "Cali"))],
    )
    sql, rows = generate(ast, db="data/tienda.db", execute=True)
    assert len(rows) > 0
