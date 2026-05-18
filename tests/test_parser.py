from pathlib import Path

from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem
from consultaES.parser import parse

RULES_PATH = Path(__file__).resolve().parent.parent / "src" / "consultaES" / "grammar" / "rules.cfg"


def _fake_items(pairs):
    return [LexicalItem(category=c, lemma=l, bindings=[]) for c, l in pairs]


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