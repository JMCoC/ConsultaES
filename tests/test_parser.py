from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem
from consultaES.parser import parse

RULES_PATH = Path(__file__).resolve().parent.parent / "src" / "consultaES" / "grammar" / "rules.cfg"


def _fake_items(pairs):
    """Return a lattice of minimal LexicalItem-compatible objects.

    Each (category, lemma) pair becomes a single-alternative position: [[item]].
    """
    return [[LexicalItem(category=c, lemma=l, bindings=[])] for c, l in pairs]


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


@pytest.mark.skip(reason="Ambigüedad cubierta en Task 4.x (Phase 4 grammar extension)")
def test_parse_returns_all_parses_when_ambiguous():
    pass
