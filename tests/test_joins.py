"""Tests para resolución automática de JOINs por FK graph."""
from consultaES.semantics.ast import SQLAst, Column, Condition, Join
from consultaES.semantics.joins import resolve_joins
from consultaES.sqlgen.emitter import emit
from consultaES.lexicon import Lexicon


def _make_lexicon():
    """Crea un Lexicon con las tablas y FKs del esquema tienda."""
    return Lexicon(
        tables={
            "clientes": ["id", "nombre", "ciudad", "tipo"],
            "vendedores": ["id", "nombre", "ciudad"],
            "productos": ["id", "nombre", "categoria", "precio"],
            "pedidos": ["id", "id_cliente", "id_vendedor", "fecha", "total"],
            "detalle_pedidos": ["id", "id_pedido", "id_producto", "cantidad", "subtotal"],
        },
        fks={
            ("pedidos", "id_cliente"): ("clientes", "id"),
            ("pedidos", "id_vendedor"): ("vendedores", "id"),
            ("detalle_pedidos", "id_pedido"): ("pedidos", "id"),
            ("detalle_pedidos", "id_producto"): ("productos", "id"),
        },
    )


# ---- Unit tests for resolve_joins ----

def test_no_join_single_table():
    """Consulta de una sola tabla no genera JOINs."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("clientes", "nombre"), Column("clientes", "ciudad")],
        tables=["clientes"],
    )
    result = resolve_joins(ast, lex)
    assert result.joins == []
    assert result.tables == ["clientes"]


def test_join_pedidos_clientes():
    """pedidos + clientes -> JOIN via id_cliente."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("pedidos", "total"), Column("clientes", "nombre")],
        tables=["pedidos"],
    )
    result = resolve_joins(ast, lex)
    assert len(result.joins) == 1
    j = result.joins[0]
    assert j.table == "clientes"
    assert j.on_left == Column("pedidos", "id_cliente")
    assert j.on_right == Column("clientes", "id")
    assert result.tables == ["pedidos"]


def test_join_productos_pedidos():
    """productos + pedidos -> JOIN through detalle_pedidos (2 JOINs)."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("productos", "nombre"), Column("pedidos", "total")],
        tables=["productos"],
    )
    result = resolve_joins(ast, lex)
    assert len(result.joins) == 2
    join_tables = [j.table for j in result.joins]
    assert "detalle_pedidos" in join_tables
    assert "pedidos" in join_tables


def test_join_three_tables():
    """Consulta que abarca clientes + pedidos + productos."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("clientes", "nombre"), Column("pedidos", "total"), Column("productos", "precio")],
        tables=["clientes"],
    )
    result = resolve_joins(ast, lex)
    # clientes -> pedidos -> detalle_pedidos -> productos = 3 joins
    assert len(result.joins) >= 3
    join_tables = [j.table for j in result.joins]
    assert "pedidos" in join_tables
    assert "detalle_pedidos" in join_tables
    assert "productos" in join_tables


def test_join_from_where_column():
    """Tabla referenciada solo en WHERE también genera JOIN."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("pedidos", "total")],
        tables=["pedidos"],
        where=[("", Condition(Column("clientes", "nombre"), "=", "Juan"))],
    )
    result = resolve_joins(ast, lex)
    assert len(result.joins) == 1
    assert result.joins[0].table == "clientes"


def test_join_from_group_by():
    """Tabla referenciada en GROUP BY genera JOIN."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("pedidos", "total", agg="SUM")],
        tables=["pedidos"],
        group_by=[Column("clientes", "ciudad")],
    )
    result = resolve_joins(ast, lex)
    assert len(result.joins) == 1
    assert result.joins[0].table == "clientes"


def test_join_from_order_by():
    """Tabla referenciada en ORDER BY genera JOIN."""
    lex = _make_lexicon()
    ast = SQLAst(
        select=[Column("pedidos", "total")],
        tables=["pedidos"],
        order_by=[(Column("clientes", "nombre"), "ASC")],
    )
    result = resolve_joins(ast, lex)
    assert len(result.joins) == 1
    assert result.joins[0].table == "clientes"


# ---- Emitter tests for JOIN syntax ----

def test_join_emitter_simple():
    """Emitter produce sintaxis JOIN correcta."""
    ast = SQLAst(
        select=[Column("pedidos", "total"), Column("clientes", "nombre")],
        tables=["pedidos"],
        joins=[
            Join(
                table="clientes",
                on_left=Column("pedidos", "id_cliente"),
                on_right=Column("clientes", "id"),
            )
        ],
    )
    sql, _ = emit(ast)
    assert "JOIN clientes ON pedidos.id_cliente = clientes.id" in sql
    assert "pedidos," not in sql  # no comma-separated tables


def test_join_emitter_multiple():
    """Emitter produce multiples JOINs en cadena."""
    ast = SQLAst(
        select=[Column("productos", "nombre"), Column("pedidos", "total")],
        tables=["productos"],
        joins=[
            Join(
                table="detalle_pedidos",
                on_left=Column("productos", "id"),
                on_right=Column("detalle_pedidos", "id_producto"),
            ),
            Join(
                table="pedidos",
                on_left=Column("detalle_pedidos", "id_pedido"),
                on_right=Column("pedidos", "id"),
            ),
        ],
    )
    sql, _ = emit(ast)
    assert "JOIN detalle_pedidos ON" in sql
    assert "JOIN pedidos ON" in sql


def test_join_emitter_with_where():
    """Emitter con JOIN + WHERE produce SQL correcto."""
    ast = SQLAst(
        select=[Column("pedidos", "total")],
        tables=["pedidos"],
        joins=[
            Join(
                table="clientes",
                on_left=Column("pedidos", "id_cliente"),
                on_right=Column("clientes", "id"),
            )
        ],
        where=[("", Condition(Column("clientes", "nombre"), "=", "Juan"))],
    )
    sql, params = emit(ast)
    assert "JOIN clientes ON" in sql
    assert "WHERE" in sql
    assert params == ["Juan"]
