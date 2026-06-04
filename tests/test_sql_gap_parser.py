from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def rig():
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    grammar = load_grammar(str(RULES_PATH))
    return lex, grammar


@pytest.mark.parametrize(
    "query",
    [
        "productos con nombre parecido a 'Mouse'",
        "productos con nombre contiene 'Mouse'",
        "productos con nombre empieza con 'M'",
        "productos con nombre termina con 'a'",
        "pedidos con total entre 100000 y 500000",
        "clientes con ciudad en 'Cali', 'Bogotá'",
        "pedidos no con total menor que 100000",
        "cuenta de clientes agrupados por ciudad con cantidad mayor que 3",
        "pedidos en marzo",
        "pedidos en 2025",
        "pedidos en 15 de abril de 2025",
        "muéstrame nombre y ciudad de clientes",
    ],
)
def test_sql_gap_queries_parse(query, rig):
    lex, grammar = rig
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, f"no parse for: {query}"
