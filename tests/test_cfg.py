from consultaES.grammar import load_grammar


def test_load_grammar_basic():
    g = load_grammar("src/consultaES/grammar/rules.cfg")
    assert g.start == "S"
    assert ("S", ("Pregunta",)) in g.productions
