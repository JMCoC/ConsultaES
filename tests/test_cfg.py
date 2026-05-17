from pathlib import Path

from consultaES.grammar import load_grammar

RULES_PATH = Path(__file__).resolve().parent.parent / "src" / "consultaES" / "grammar" / "rules.cfg"


def test_load_grammar_basic():
    g = load_grammar(str(RULES_PATH))
    assert g.start == "S"
    assert ("S", ("Pregunta",)) in g.productions
