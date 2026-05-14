from consultaES.lexicon import build_lexicon, categorize
from consultaES.tokenizer import tokenize


def test_lexicon_has_tables_and_columns():
    lex = build_lexicon("data/schema.sql")
    assert "clientes" in lex.tables
    assert "ciudad" in lex.columns_of("clientes")


def test_lexicon_has_fks():
    lex = build_lexicon("data/schema.sql")
    assert lex.fks[("pedidos", "id_cliente")] == ("clientes", "id")


def test_lexicon_values_include_seed_cities():
    lex = build_lexicon("data/schema.sql")
    assert "Cali" in lex.values["ciudad"]


def test_categorize_binds_entities():
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("cuántos clientes de Cali")
    items = categorize(toks, lex)
    kinds = [i.category for i in items]
    assert "INTERROG" in kinds
    assert "N_TABLA" in kinds
    assert "VALOR_CIUDAD" in kinds


def test_juan_is_ambiguous():
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("ventas de Juan")
    items = categorize(toks, lex)
    juan_items = [i for i in items if i.lemma.lower() == "juan"]
    assert len(juan_items) >= 2, f"expected ambiguity on Juan, got {juan_items}"
