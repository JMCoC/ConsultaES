from consultaES.tokenizer.dfa import DFA


def test_dfa_accepts_integer():
    d = DFA(
        states={"q0", "q1"},
        alphabet=set("0123456789"),
        delta={("q0", c): "q1" for c in "0123456789"}
        | {("q1", c): "q1" for c in "0123456789"},
        start="q0",
        finals={"q1"},
    )
    assert d.longest_match("123abc") == 3
    assert d.longest_match("abc") == 0
