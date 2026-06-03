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
    kinds = [item.category for pos in lattice for item in pos]
    assert "INTERROG" in kinds
    assert "N_TABLA" in kinds
    assert "VALOR_CIUDAD" in kinds

def test_categorize_preserves_sql_gap_markers():
    lex = build_lexicon("data/schema.sql", "data/tienda.db")
    tokens = tokenize("productos con nombre parecido a 'Mouse'")
    lattice = categorize(tokens, lex)
    categories = [item.category for alternatives in lattice for item in alternatives]
    assert "OP_LIKE" in categories


def test_categorize_between_and_negation_markers():
    lex = build_lexicon("data/schema.sql", "data/tienda.db")
    tokens = tokenize("pedidos no con total entre 100 y 500")
    lattice = categorize(tokens, lex)
    categories = [item.category for alternatives in lattice for item in alternatives]
    assert "NEG" in categories
    assert "RANGO" in categories

def test_juan_is_ambiguous():
    lex = build_lexicon("data/schema.sql")
    toks = tokenize("ventas de Juan")
    lattice = categorize(toks, lex)
    juan_pos = lattice[-1]
    juan_items = [i for i in juan_pos if i.lemma.lower() == "juan"]
    assert len(juan_items) >= 2, f"expected ambiguity on Juan, got {juan_items}"


def test_categorize_lattice_length_matches_tokens():
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
    juan_alts = lattice[3]
    assert len(juan_alts) >= 2
    assert all(item.category == "VALOR_NOMBRE" for item in juan_alts)
