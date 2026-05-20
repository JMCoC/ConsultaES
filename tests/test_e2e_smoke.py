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
    g = load_grammar(str(RULES_PATH))
    return lex, g


@pytest.mark.parametrize(
    "q",
    [
        "cuántos clientes",
        "muéstrame los clientes",
        "cuántos clientes con ciudad igual a 'Cali'",
        "qué productos",
        "lista los pedidos",
    ],
)
def test_smoke(q, rig):
    lex, g = rig
    tokens = tokenize(q)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {q}"
