from __future__ import annotations

from pathlib import Path

import pytest

from consultaES.disambiguator import (
    Context,
    DisambiguationRequest,
    disambiguate,
    score,
)
from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem, Lexicon, build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def lex() -> Lexicon:
    return build_lexicon(str(SCHEMA_PATH), str(DB_PATH))


@pytest.fixture(scope="module")
def grammar():
    return load_grammar(str(RULES_PATH))


def _filtro_tree(col_name: str, op: str, val_leaf: LexicalItem,
                 col_bindings=None) -> ParseTree:
    prep = LexicalItem("PREP", "con")
    col = LexicalItem(
        "N_COLUMNA",
        col_name,
        bindings=col_bindings or [],
    )
    op_leaf = LexicalItem("OP_COMP", op)
    valor = ParseTree("Valor", [val_leaf])
    return ParseTree("Filtro", [prep, col, op_leaf, valor])


def _sn(table: str) -> ParseTree:
    n_tabla = LexicalItem("N_TABLA", table, bindings=[(table, None)])
    return ParseTree("SN", [n_tabla])

def test_schema_existence_all_valid(lex):
    sn = _sn("clientes")
    juan = LexicalItem("VALOR_NOMBRE", "Juan", bindings=[("clientes", "nombre")])
    tree = ParseTree("S", [ParseTree("Pregunta", [sn, juan])])

    s = score(tree, Context(), lex, db_path=None)
    assert s >= 3

def test_schema_existence_fabricated_binding(lex):
    sn = _sn("clientes")
    fake = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[("tabla_inventada", "col_x")]
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn, fake])])

    s = score(tree, Context(), lex, db_path=None)
    assert s == 0

def test_type_compat_numeric_ok(lex):
    sn = _sn("pedidos")
    num_leaf = LexicalItem("NUM", "100000")
    filtro = _filtro_tree(
        "total", "mayor que", num_leaf,
        col_bindings=[("pedidos", "total")],
    )
    filtros = ParseTree("Filtros", [filtro])
    tree = ParseTree("S", [ParseTree("Pregunta", [sn, filtros])])

    s = score(tree, Context(), lex, db_path=None)
    assert s >= 5


def test_type_compat_text_with_number_no_bonus(lex):
    sn = _sn("clientes")
    num_leaf = LexicalItem("NUM", "100")
    filtro = _filtro_tree(
        "ciudad", "igual a", num_leaf,
        col_bindings=[("clientes", "ciudad")],
    )
    filtros = ParseTree("Filtros", [filtro])
    tree = ParseTree("S", [ParseTree("Pregunta", [sn, filtros])])

    s = score(tree, Context(), lex, db_path=None)
    assert s == 4

def test_right_attachment_bonus(lex):
    sn = _sn("clientes")
    val_leaf = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    filtro = _filtro_tree(
        "ciudad", "igual a", val_leaf,
        col_bindings=[("clientes", "ciudad")],
    )
    filtros = ParseTree("Filtros", [filtro])

    right_tree = ParseTree("S", [ParseTree("Pregunta", [sn, filtros])])
    left_tree = ParseTree("S", [ParseTree("Pregunta", [filtros, sn])])

    s_right = score(right_tree, Context(), lex, db_path=None)
    s_left = score(left_tree, Context(), lex, db_path=None)
    assert s_right > s_left
    assert (s_right - s_left) >= 1


def test_value_frequency_bonus_with_db(lex):
    sn = _sn("clientes")
    cali = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    filtro = _filtro_tree(
        "ciudad", "igual a", cali,
        col_bindings=[("clientes", "ciudad")],
    )
    filtros = ParseTree("Filtros", [filtro])
    tree = ParseTree("S", [ParseTree("Pregunta", [sn, filtros])])

    s_db = score(tree, Context(), lex, db_path=str(DB_PATH))
    s_nodb = score(tree, Context(), lex, db_path=None)
    assert s_db >= s_nodb


def test_zero_rows_penalty(lex):
    sn = _sn("clientes")
    cali = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    filtro_ok = _filtro_tree(
        "ciudad", "igual a", cali,
        col_bindings=[("clientes", "ciudad")],
    )
    filtros_ok = ParseTree("Filtros", [filtro_ok])
    tree_ok = ParseTree("S", [ParseTree("Pregunta", [sn, filtros_ok])])

    atlantis = LexicalItem(
        "VALOR_CIUDAD", "Atlantis", bindings=[("clientes", "ciudad")]
    )
    filtro_empty = _filtro_tree(
        "ciudad", "igual a", atlantis,
        col_bindings=[("clientes", "ciudad")],
    )
    filtros_empty = ParseTree("Filtros", [filtro_empty])
    tree_empty = ParseTree("S", [ParseTree("Pregunta", [sn, filtros_empty])])

    s_ok = score(tree_ok, Context(), lex, db_path=str(DB_PATH))
    s_empty = score(tree_empty, Context(), lex, db_path=str(DB_PATH))
    assert s_ok > s_empty

def test_disambiguate_returns_top_when_margin(lex):
    sn = _sn("clientes")

    cali = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    filtro_a = _filtro_tree(
        "ciudad", "igual a", cali,
        col_bindings=[("clientes", "ciudad")],
    )
    tree_a = ParseTree(
        "S", [ParseTree("Pregunta", [sn, ParseTree("Filtros", [filtro_a])])]
    )

    num_leaf = LexicalItem("NUM", "9999")
    filtro_b = _filtro_tree(
        "ciudad", "igual a", num_leaf,
        col_bindings=[("clientes", "ciudad")],
    )
    tree_b = ParseTree(
        "S", [ParseTree("Pregunta", [sn, ParseTree("Filtros", [filtro_b])])]
    )

    out = disambiguate([tree_a, tree_b], lex, db_path=str(DB_PATH))
    assert out is tree_a


def test_disambiguate_returns_request_when_tied(lex):
    sn = _sn("clientes")
    val = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    f = _filtro_tree(
        "ciudad", "igual a", val,
        col_bindings=[("clientes", "ciudad")],
    )
    tree_a = ParseTree(
        "S", [ParseTree("Pregunta", [sn, ParseTree("Filtros", [f])])]
    )
    tree_b = ParseTree(
        "S", [ParseTree("Pregunta", [sn, ParseTree("Filtros", [f])])]
    )

    out = disambiguate([tree_a, tree_b], lex, db_path=str(DB_PATH))
    assert isinstance(out, DisambiguationRequest)
    assert len(out.options) >= 2
    for opt in out.options:
        assert len(opt) == 2


def test_disambiguate_returns_none_when_layer1_prunes_all():
    iso_lex = Lexicon(
        tables={"productos": ["id", "nombre"], "vendedores": ["id", "nombre"]},
        fks={},
        values={},
        values_by_table={},
    )
    sn_productos = ParseTree(
        "SN",
        [
            ParseTree(
                "N_TABLA",
                [LexicalItem("N_TABLA", "productos", bindings=[("productos", None)])],
            )
        ],
    )
    bad = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[("vendedores", "nombre")]
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn_productos, bad])])
    assert disambiguate([tree], iso_lex, db_path=None) is None


def test_disambiguate_real_pipeline(lex, grammar):
    tokens = tokenize("cuántos clientes")
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees
    out = disambiguate(trees, lex, db_path=str(DB_PATH))
    assert isinstance(out, ParseTree)
