from consultaES.tokenizer import tokenize, Token


def kinds(texto):
    return [t.kind for t in tokenize(texto)]


def test_numbers():
    assert kinds("100000 3.5") == ["NUM", "NUM"]


def test_dates_mes_solo():
    assert kinds("marzo") == ["FECHA"]


def test_dates_full():
    assert kinds("15 de abril de 2025") == ["FECHA"]


def test_dates_year_or_num():
    assert kinds("2025") == ["FECHA"]


def test_comparador_compuesto():
    assert kinds("mayor que 100") == ["OP_COMP", "NUM"]
    assert kinds("menor o igual a 5") == ["OP_COMP", "NUM"]


def test_palabra_with_accents():
    assert kinds("cuántos") == ["PALABRA"]


def test_cadena():
    assert kinds("'Cali'") == ["CADENA"]


def test_conector_y_punt():
    assert kinds("a y b, c") == ["PALABRA", "CONECTOR", "PALABRA", "PUNT", "PALABRA"]


def test_unknown_char_emits_error():
    tokens = tokenize("abc @@@ def")
    assert any(t.kind == "ERROR" for t in tokens)


def test_token_positions():
    toks = tokenize("hola mundo")
    assert toks[0].start == 0 and toks[0].end == 4
    assert toks[1].start == 5 and toks[1].end == 10
