from pathlib import Path
import sqlite3

import pytest

from consultaES.disambiguator import Context, DisambiguationRequest, disambiguate
from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.semantics import prepare_sql_ast, interpret
from consultaES.sqlgen import generate
from consultaES.sqlgen.emitter import emit
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
SEED_PATH = ROOT / "data" / "seed.sql"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "tienda.db"
    con = sqlite3.connect(path)
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.executescript(SEED_PATH.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()
    return path


@pytest.fixture(scope="module")
def rig(db_path):
    lex = build_lexicon(str(SCHEMA_PATH), str(db_path))
    grammar = load_grammar(str(RULES_PATH))
    return lex, grammar, db_path


def norm(sql: str) -> str:
    return " ".join(sql.lower().split())


def expected_rows(db_path: Path, sql: str, params=()):
    con = sqlite3.connect(db_path)
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def consultar(query: str, rig):
    lex, grammar, db_path = rig
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, f"no parse for: {query}"
    selected = disambiguate(trees, lex, Context(), db_path=str(db_path))
    if isinstance(selected, DisambiguationRequest):
        pytest.fail(f"canonical query required disambiguation: {query}")
    ast = prepare_sql_ast(interpret(selected), lex)
    sql, params = emit(ast)
    generated_sql, rows = generate(ast, db=str(db_path))
    assert generated_sql == sql
    return sql, params, rows


@pytest.mark.parametrize(
    ("query", "sql_expected", "params"),
    [
        (
            "productos con nombre parecido a 'Mouse'",
            "SELECT productos.* FROM productos WHERE nombre LIKE ?",
            ("%Mouse%",),
        ),
        (
            "productos con nombre empieza con 'M'",
            "SELECT productos.* FROM productos WHERE nombre LIKE ?",
            ("M%",),
        ),
        (
            "pedidos con total entre 100000 y 500000",
            "SELECT pedidos.* FROM pedidos WHERE total BETWEEN ? AND ?",
            (100000, 500000),
        ),
        (
            "pedidos en marzo",
            "SELECT pedidos.* FROM pedidos WHERE pedidos.fecha BETWEEN ? AND ?",
            ("2025-03-01", "2025-03-31"),
        ),
        (
            "clientes con ciudad en 'Cali', 'Bogotá'",
            "SELECT clientes.* FROM clientes WHERE ciudad IN (?, ?)",
            ("Cali", "Bogotá"),
        ),
        (
            "pedidos no con total menor que 100000",
            "SELECT pedidos.* FROM pedidos WHERE NOT total < ?",
            (100000,),
        ),
        (
            "pedidos en 2025",
            "SELECT pedidos.* FROM pedidos WHERE pedidos.fecha BETWEEN ? AND ?",
            ("2025-01-01", "2025-12-31"),
        ),
        (
            "pedidos en 15 de abril de 2025",
            "SELECT pedidos.* FROM pedidos WHERE pedidos.fecha BETWEEN ? AND ?",
            ("2025-04-15", "2025-04-15"),
        ),
    ],
)
def test_sql_gap_where_e2e(query, sql_expected, params, rig):
    sql, generated_params, rows = consultar(query, rig)
    _, _, db_path = rig
    assert norm(sql) == norm(sql_expected)
    assert generated_params == list(params)
    assert rows == expected_rows(db_path, sql_expected, params)


def test_having_count_e2e(rig):
    query = "cuenta de clientes agrupados por ciudad con cantidad mayor que 3"
    expected_sql = "SELECT COUNT(*) FROM clientes GROUP BY ciudad HAVING COUNT(*) > ?"
    sql, params, rows = consultar(query, rig)
    _, _, db_path = rig
    assert norm(sql) == norm(expected_sql)
    assert params == [3]
    assert rows == expected_rows(db_path, expected_sql, (3,))


def test_having_sum_e2e(rig):
    query = "suma de total de pedidos agrupados por fecha con suma mayor que 500000"
    expected_sql = (
        "SELECT SUM(pedidos.total) FROM pedidos "
        "GROUP BY fecha HAVING SUM(pedidos.total) > ?"
    )
    sql, params, rows = consultar(query, rig)
    _, _, db_path = rig
    assert norm(sql) == norm(expected_sql)
    assert params == [500000]
    assert rows == expected_rows(db_path, expected_sql, (500000,))


@pytest.mark.parametrize(
    ("query", "expected_sql"),
    [
        (
            "muéstrame nombre y ciudad de clientes",
            "SELECT clientes.nombre, clientes.ciudad FROM clientes",
        ),
        (
            "muéstrame nombre de productos",
            "SELECT productos.nombre FROM productos",
        ),
    ],
)
def test_projection_e2e(query, expected_sql, rig):
    sql, params, rows = consultar(query, rig)
    _, _, db_path = rig
    assert norm(sql) == norm(expected_sql)
    assert params == []
    assert rows == expected_rows(db_path, expected_sql)
