from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem, build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.tokenizer import tokenize

RULES_PATH = Path(__file__).resolve().parent.parent / "src" / "consultaES" / "grammar" / "rules.cfg"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "data" / "schema.sql"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "tienda.db"

def _fake_items(pairs):
    return [[LexicalItem(category=c, lemma=lemma, bindings=[])] for c, lemma in pairs]


def test_parse_simple_accepting():
    G = load_grammar(str(RULES_PATH))
    items = _fake_items([("INTERROG", "cuántos"), ("N_TABLA", "clientes")])
    trees = parse(items, G)
    assert len(trees) >= 1
    assert trees[0].label == "S"


def test_parse_rejects_bad_input():
    G = load_grammar(str(RULES_PATH))
    items = _fake_items([("N_TABLA", "clientes"), ("INTERROG", "cuántos")])
    assert parse(items, G) == []


def test_parse_ambiguous_lattice():
    """An ambiguous lattice position should not inflate the token count."""
    G = load_grammar(str(RULES_PATH))
    # Simulate: "cuántos clientes" where "clientes" has two interpretations
    items = [
        [LexicalItem(category="INTERROG", lemma="cuántos", bindings=[])],
        [
            LexicalItem(category="N_TABLA", lemma="clientes", bindings=[]),
            LexicalItem(category="N_COLUMNA", lemma="clientes", bindings=[]),
        ],
    ]
    trees = parse(items, G)
    # Should still parse (N_TABLA is the one the grammar uses)
    assert len(trees) >= 1
    assert trees[0].label == "S"

def _leaves(node):
    if isinstance(node, LexicalItem):
        return [node]
    if isinstance(node, ParseTree):
        result = []
        for child in node.children:
            result.extend(_leaves(child))
        return result
    return []


def test_parse_ventas_de_juan_preserves_lexical_binding_ambiguity():
    G = load_grammar(str(RULES_PATH))
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    items = categorize(tokenize("ventas de Juan"), lex)

    trees = parse(items, G)

    juan_bindings = {
        tuple(leaf.bindings)
        for tree in trees
        for leaf in _leaves(tree)
        if leaf.category == "VALOR_NOMBRE" and leaf.lemma.lower() == "juan"
    }
    assert len(trees) >= 2
    assert (("clientes", "nombre"),) in juan_bindings
    assert (("vendedores", "nombre"),) in juan_bindings


@pytest.mark.skip(reason="Ambigüedad cubierta en Task 4.x (Phase 4 grammar extension)")
def test_parse_returns_all_parses_when_ambiguous():
    pass
