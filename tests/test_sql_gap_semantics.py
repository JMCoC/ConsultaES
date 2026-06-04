from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.semantics import SQLAst, interpret
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


def _interpret(query: str, rig) -> SQLAst:
    lex, grammar = rig
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, f"no parse for: {query}"
    return interpret(trees[0])


@pytest.mark.parametrize(
    ("query", "expected_pattern"),
    [
        ("productos con nombre parecido a 'Mouse'", "%Mouse%"),
        ("productos con nombre contiene 'Mouse'", "%Mouse%"),
        ("productos con nombre empieza con 'M'", "M%"),
        ("productos con nombre termina con 'a'", "%a"),
    ],
)
def test_like_conditions(query, expected_pattern, rig):
    ast = _interpret(query, rig)
    assert ast.tables == ["productos"]
    assert len(ast.where) == 1
    _, cond = ast.where[0]
    assert cond.col.name == "nombre"
    assert cond.op == "LIKE"
    assert cond.value == expected_pattern


def test_between_condition(rig):
    ast = _interpret("pedidos con total entre 100000 y 500000", rig)
    assert ast.tables == ["pedidos"]
    _, cond = ast.where[0]
    assert cond.col.name == "total"
    assert cond.op == "BETWEEN"
    assert cond.value == (100000, 500000)


def test_in_condition(rig):
    ast = _interpret("clientes con ciudad en 'Cali', 'Bogotá'", rig)
    assert ast.tables == ["clientes"]
    _, cond = ast.where[0]
    assert cond.col.name == "ciudad"
    assert cond.op == "IN"
    assert cond.value == ["Cali", "Bogotá"]


def test_negated_condition(rig):
    ast = _interpret("pedidos no con total menor que 100000", rig)
    assert ast.tables == ["pedidos"]
    _, cond = ast.where[0]
    assert cond.col.name == "total"
    assert cond.op == "<"
    assert cond.value == 100000
    assert cond.negated is True


def test_having_count_after_group_by(rig):
    ast = _interpret("cuenta de clientes agrupados por ciudad con cantidad mayor que 3", rig)
    assert ast.tables == ["clientes"]
    assert ast.group_by[0].name == "ciudad"
    assert len(ast.having) == 1
    _, cond = ast.having[0]
    assert cond.col.agg == "COUNT"
    assert cond.col.name == "*"
    assert cond.op == ">"
    assert cond.value == 3


def test_having_sum_after_group_by(rig):
    ast = _interpret("suma de total de pedidos agrupados por fecha con suma mayor que 500000", rig)
    assert ast.tables == ["pedidos"]
    assert ast.group_by[0].name == "fecha"
    assert len(ast.having) == 1
    _, cond = ast.having[0]
    assert cond.col.agg == "SUM"
    assert cond.col.table == "pedidos"
    assert cond.col.name == "total"
    assert cond.op == ">"
    assert cond.value == 500000
