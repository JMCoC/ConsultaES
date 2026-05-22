"""Tests para Fase 4.1a: agregaciones, GROUP BY, ORDER BY, LIMIT."""

from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.semantics import Column, Condition, SQLAst, interpret
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def rig():
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    g = load_grammar(str(RULES_PATH))
    return lex, g


def _interpret(q: str, rig) -> SQLAst:
    lex, g = rig
    tokens = tokenize(q)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {q}"
    return interpret(trees[0])


# =====================================================================
# Agregaciones
# =====================================================================


def test_promedio_de_precio_de_productos(rig):
    """'promedio de precio de productos' -> AVG(precio) FROM productos"""
    ast = _interpret("promedio de precio de productos", rig)
    assert ast.tables == ["productos"]
    assert len(ast.select) == 1
    assert ast.select[0].agg == "AVG"
    assert ast.select[0].name == "precio"


def test_suma_de_total_de_pedidos(rig):
    """'muéstrame la suma de total de pedidos' -> SUM(total) FROM pedidos"""
    ast = _interpret("muéstrame la suma de total de pedidos", rig)
    assert ast.tables == ["pedidos"]
    assert len(ast.select) == 1
    assert ast.select[0].agg == "SUM"
    assert ast.select[0].name == "total"


def test_cuenta_de_clientes(rig):
    """'cuenta de clientes' -> COUNT(*) FROM clientes"""
    ast = _interpret("cuenta de clientes", rig)
    assert ast.tables == ["clientes"]
    assert len(ast.select) == 1
    assert ast.select[0].agg == "COUNT"


def test_maximo_de_precio_de_productos(rig):
    """'máximo de precio de productos' -> MAX(precio) FROM productos"""
    ast = _interpret("máximo de precio de productos", rig)
    assert ast.tables == ["productos"]
    assert len(ast.select) == 1
    assert ast.select[0].agg == "MAX"
    assert ast.select[0].name == "precio"


def test_minimo_de_total_de_pedidos(rig):
    """'mínimo de total de pedidos' -> MIN(total) FROM pedidos"""
    ast = _interpret("mínimo de total de pedidos", rig)
    assert ast.tables == ["pedidos"]
    assert len(ast.select) == 1
    assert ast.select[0].agg == "MIN"
    assert ast.select[0].name == "total"


def test_agg_con_filtro(rig):
    """'máximo de total de pedidos con total mayor que 100' -> MAX(total) WHERE total > 100"""
    ast = _interpret("máximo de total de pedidos con total mayor que 100", rig)
    assert ast.tables == ["pedidos"]
    assert ast.select[0].agg == "MAX"
    assert ast.select[0].name == "total"
    assert len(ast.where) == 1
    _, cond = ast.where[0]
    assert cond.op == ">"
    assert cond.value == 100


def test_agg_sin_columna(rig):
    """'cuenta de clientes' -> COUNT(*) con agg=COUNT, name=*"""
    ast = _interpret("cuenta de clientes", rig)
    assert ast.select[0].agg == "COUNT"
    assert ast.select[0].name == "*"


# =====================================================================
# GROUP BY
# =====================================================================


def test_agrupados_por(rig):
    """'cuántos clientes agrupados por ciudad' -> GROUP BY ciudad"""
    ast = _interpret("cuántos clientes agrupados por ciudad", rig)
    assert ast.tables == ["clientes"]
    assert len(ast.group_by) == 1
    assert ast.group_by[0].name == "ciudad"


def test_agg_agrupados_por(rig):
    """'cuenta de clientes agrupados por ciudad' -> COUNT(*) GROUP BY ciudad"""
    ast = _interpret("cuenta de clientes agrupados por ciudad", rig)
    assert ast.tables == ["clientes"]
    assert ast.select[0].agg == "COUNT"
    assert len(ast.group_by) == 1
    assert ast.group_by[0].name == "ciudad"


# =====================================================================
# ORDER BY
# =====================================================================


def test_ordenados_por(rig):
    """'muéstrame los productos ordenados por precio' -> ORDER BY precio ASC"""
    ast = _interpret("muéstrame los productos ordenados por precio", rig)
    assert ast.tables == ["productos"]
    assert len(ast.order_by) == 1
    col, direction = ast.order_by[0]
    assert col.name == "precio"
    assert direction == "ASC"


def test_ordenados_por_descendente(rig):
    """'muéstrame los productos ordenados por precio descendente' -> ORDER BY precio DESC"""
    ast = _interpret(
        "muéstrame los productos ordenados por precio descendente", rig
    )
    assert ast.tables == ["productos"]
    assert len(ast.order_by) == 1
    col, direction = ast.order_by[0]
    assert col.name == "precio"
    assert direction == "DESC"


def test_ordenados_por_ascendente(rig):
    """'muéstrame los productos ordenados por precio ascendente' -> ORDER BY precio ASC"""
    ast = _interpret(
        "muéstrame los productos ordenados por precio ascendente", rig
    )
    assert len(ast.order_by) == 1
    col, direction = ast.order_by[0]
    assert col.name == "precio"
    assert direction == "ASC"


# =====================================================================
# LIMIT
# =====================================================================


def test_limit_det_num(rig):
    """'muéstrame los 5 productos' -> LIMIT 5"""
    ast = _interpret("muéstrame los 5 productos", rig)
    assert ast.tables == ["productos"]
    assert ast.limit == 5


def test_limit_con_filtro(rig):
    """'muéstrame los 3 pedidos con total mayor que 100' -> LIMIT 3, WHERE"""
    ast = _interpret("muéstrame los 3 pedidos con total mayor que 100", rig)
    assert ast.tables == ["pedidos"]
    assert ast.limit == 3
    assert len(ast.where) == 1


# =====================================================================
# Combinaciones
# =====================================================================


def test_agg_filtro_agrupacion(rig):
    """'cuenta de clientes con tipo igual a 'premium' agrupados por ciudad'"""
    ast = _interpret(
        "cuenta de clientes con tipo igual a 'premium' agrupados por ciudad",
        rig,
    )
    assert ast.tables == ["clientes"]
    assert ast.select[0].agg == "COUNT"
    assert len(ast.where) == 1
    assert len(ast.group_by) == 1
    assert ast.group_by[0].name == "ciudad"


def test_agrupados_y_ordenados(rig):
    """ORDER BY + GROUP BY combined"""
    ast = _interpret("cuenta de clientes agrupados por ciudad ordenados por ciudad", rig)
    assert len(ast.group_by) == 1
    assert len(ast.order_by) == 1


def test_orden_con_filtro(rig):
    """'muéstrame los pedidos con total mayor que 100 ordenados por total'"""
    ast = _interpret(
        "muéstrame los pedidos con total mayor que 100 ordenados por total",
        rig,
    )
    assert ast.tables == ["pedidos"]
    assert len(ast.where) == 1
    assert len(ast.order_by) == 1
    assert ast.order_by[0][0].name == "total"


# =====================================================================
# Parse-only smoke tests (queries must parse but semantic details not checked)
# =====================================================================


@pytest.mark.parametrize(
    "q",
    [
        "promedio de precio de productos",
        "suma de total de pedidos",
        "cuenta de clientes",
        "máximo de precio de productos",
        "mínimo de total de pedidos",
        "cuántos clientes agrupados por ciudad",
        "muéstrame los productos ordenados por precio",
        "muéstrame los productos ordenados por precio descendente",
        "muéstrame los 5 productos",
    ],
)
def test_parse_smoke(q, rig):
    """Todas las nuevas consultas deben tener al menos un parse."""
    lex, g = rig
    tokens = tokenize(q)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {q}"
