import re
from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.semantics import interpret, prepare_sql_ast
from consultaES.sqlgen import generate
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


def norm(sql: str) -> str:
    """Normaliza SQL: minúsculas y espacios colapsados."""
    return re.sub(r"\s+", " ", sql.lower()).strip()


@pytest.fixture(scope="module")
def rig():
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    g = load_grammar(str(RULES_PATH))
    return lex, g


def _sql(query: str, rig) -> str:
    """Ejecuta el pipeline completo y devuelve el SQL normalizado."""
    lex, g = rig
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {query}"
    ast = prepare_sql_ast(interpret(trees[0]), lex)
    sql, _params = generate(ast, db=None, execute=False)
    return norm(sql)

def _leaves(node):
    if hasattr(node, "category"):
        return [node]
    if isinstance(node, ParseTree):
        leaves = []
        for child in node.children:
            leaves.extend(_leaves(child))
        return leaves
    return []


def _tree_with_value_binding(query: str, binding: tuple[str, str], rig):
    lex, g = rig
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {query}"
    for tree in trees:
        for leaf in _leaves(tree):
            if leaf.category.startswith("VALOR_") and binding in leaf.bindings:
                return tree
    raise AssertionError(f"no tree for {query!r} with binding {binding!r}")


def test_ventas_de_juan_cliente_genera_join_y_ejecuta(rig):
    tree = _tree_with_value_binding("ventas de Juan", ("clientes", "nombre"), rig)
    lex, _g = rig
    ast = prepare_sql_ast(interpret(tree), lex)

    sql, rows = generate(ast, db=str(DB_PATH), execute=True)

    normalized = norm(sql)
    assert "from pedidos join clientes" in normalized
    assert "pedidos.id_cliente = clientes.id" in normalized
    assert "where clientes.nombre = ?" in normalized
    assert rows

# =====================================================================
# Simple SELECT (4 consultas)
# =====================================================================

_SIMPLE_SELECT = [
    pytest.param(
        "cuántos clientes",
        ["select", "clientes", "from clientes"],
        id="cuantos-clientes",
    ),
    pytest.param(
        "muéstrame los productos",
        ["select", "productos", "from productos"],
        id="muestrame-productos",
    ),
    pytest.param(
        "qué vendedores",
        ["select", "vendedores", "from vendedores"],
        id="que-vendedores",
    ),
    pytest.param(
        "lista los pedidos",
        ["select", "pedidos", "from pedidos"],
        id="lista-pedidos",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _SIMPLE_SELECT)
def test_simple_select(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# SELECT con WHERE (4 consultas)
# =====================================================================

_WHERE = [
    pytest.param(
        "cuántos clientes con ciudad igual a 'Cali'",
        ["from clientes", "where", "ciudad", "=", "?"],
        id="where-ciudad-cali",
    ),
    pytest.param(
        "muéstrame los pedidos con total mayor que 100000",
        ["from pedidos", "where", "total", ">", "?"],
        id="where-total-mayor",
    ),
    pytest.param(
        "lista los productos con precio menor que 50000",
        ["from productos", "where", "precio", "<", "?"],
        id="where-precio-menor",
    ),
    pytest.param(
        "muéstrame los clientes con tipo igual a 'premium'",
        ["from clientes", "where", "tipo", "=", "?"],
        id="where-tipo-premium",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _WHERE)
def test_where(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# Agregaciones (5 consultas)
# =====================================================================

_AGGREGATIONS = [
    pytest.param(
        "cuenta de clientes",
        ["select count(", "from clientes"],
        id="count-clientes",
    ),
    pytest.param(
        "suma de total de pedidos",
        ["select sum(", "total", "from pedidos"],
        id="sum-total-pedidos",
    ),
    pytest.param(
        "promedio de precio de productos",
        ["select avg(", "precio", "from productos"],
        id="avg-precio-productos",
    ),
    pytest.param(
        "máximo de total de pedidos",
        ["select max(", "total", "from pedidos"],
        id="max-total-pedidos",
    ),
    pytest.param(
        "mínimo de total de pedidos",
        ["select min(", "total", "from pedidos"],
        id="min-total-pedidos",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _AGGREGATIONS)
def test_aggregations(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# GROUP BY (3 consultas)
# =====================================================================

_GROUP_BY = [
    pytest.param(
        "cuántos clientes agrupados por ciudad",
        ["from clientes", "group by", "ciudad"],
        id="group-by-ciudad",
    ),
    pytest.param(
        "cuenta de clientes agrupados por tipo",
        ["select count(", "from clientes", "group by", "tipo"],
        id="count-group-by-tipo",
    ),
    pytest.param(
        "cuenta de clientes agrupados por ciudad",
        ["select count(", "from clientes", "group by", "ciudad"],
        id="count-group-by-ciudad",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _GROUP_BY)
def test_group_by(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# ORDER BY (3 consultas)
# =====================================================================

_ORDER_BY = [
    pytest.param(
        "muéstrame los productos ordenados por precio",
        ["from productos", "order by", "precio", "asc"],
        id="order-by-precio-asc",
    ),
    pytest.param(
        "muéstrame los productos ordenados por precio descendente",
        ["from productos", "order by", "precio", "desc"],
        id="order-by-precio-desc",
    ),
    pytest.param(
        "muéstrame los productos ordenados por precio ascendente",
        ["from productos", "order by", "precio", "asc"],
        id="order-by-precio-asc-explicit",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _ORDER_BY)
def test_order_by(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# LIMIT (2 consultas)
# =====================================================================

_LIMIT = [
    pytest.param(
        "muéstrame los 5 productos",
        ["from productos", "limit 5"],
        id="limit-5-productos",
    ),
    pytest.param(
        "muéstrame los 3 pedidos",
        ["from pedidos", "limit 3"],
        id="limit-3-pedidos",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _LIMIT)
def test_limit(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"


# =====================================================================
# Combinaciones (5 consultas)
# =====================================================================

_COMBINATIONS = [
    pytest.param(
        "muéstrame los pedidos con total mayor que 100 ordenados por total",
        ["from pedidos", "where", "total", ">", "order by", "total"],
        id="where-order-by",
    ),
    pytest.param(
        "cuenta de clientes con tipo igual a 'premium' agrupados por ciudad",
        ["select count(", "from clientes", "where", "tipo", "=", "group by", "ciudad"],
        id="agg-where-group-by",
    ),
    pytest.param(
        "muéstrame los 5 productos ordenados por precio descendente",
        ["from productos", "order by", "precio", "desc", "limit 5"],
        id="limit-order-by-desc",
    ),
    pytest.param(
        "máximo de total de pedidos con total mayor que 100",
        ["select max(", "total", "from pedidos", "where", "total", ">"],
        id="agg-where",
    ),
    pytest.param(
        "cuenta de clientes agrupados por ciudad ordenados por ciudad",
        ["select count(", "from clientes", "group by", "ciudad", "order by", "ciudad"],
        id="agg-group-by-order-by",
    ),
]


@pytest.mark.parametrize("query, expected_fragments", _COMBINATIONS)
def test_combinations(query, expected_fragments, rig):
    sql = _sql(query, rig)
    for frag in expected_fragments:
        assert frag in sql, f"'{frag}' no encontrado en SQL: {sql}"
