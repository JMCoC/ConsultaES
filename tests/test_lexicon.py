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
    lattice = categorize(toks, lex)
    # Flatten to check categories present
    kinds = [item.category for pos in lattice for item in pos]
    assert "INTERROG" in kinds
    assert "N_TABLA" in kinds
    assert "VALOR_CIUDAD" in kinds


def test_juan_is_ambiguous():
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("ventas de Juan")
    lattice = categorize(toks, lex)
    # "Juan" is the last position; it should have >=2 alternatives in a single slot
    juan_pos = lattice[-1]
    juan_items = [i for i in juan_pos if i.lemma.lower() == "juan"]
    assert len(juan_items) >= 2, f"expected ambiguity on Juan, got {juan_items}"


def test_categorize_lattice_length_matches_tokens():
    """Lattice has exactly one position per input token, even for ambiguous tokens."""
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("muéstrame clientes de Juan")
    lattice = categorize(toks, lex)
    assert len(lattice) == len(toks), (
        f"lattice length {len(lattice)} != token count {len(toks)}"
    )


def test_categorize_ambiguous_name():
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("muéstrame clientes de Juan")
    lattice = categorize(toks, lex)
    # 4 tokens -> 4 positions
    assert len(lattice) == 4
    # "Juan" is the last position and should have >=2 alternatives (vendedor + cliente)
    juan_alts = lattice[3]
    assert len(juan_alts) >= 2
    assert all(item.category == "VALOR_NOMBRE" for item in juan_alts)
