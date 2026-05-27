from __future__ import annotations

from pathlib import Path

import pytest

from consultaES.disambiguator import prune_by_typing
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

def _sn_tree(table: str, leaves_after_table: list | None = None) -> ParseTree:
    n_tabla = LexicalItem("N_TABLA", table, bindings=[(table, None)])
    children = [ParseTree("N_TABLA", [n_tabla])]
    if leaves_after_table:
        children.extend(leaves_after_table)
    return ParseTree("SN", children)


def test_unambiguous_tree_passes_through(lex, grammar):
    tokens = tokenize("cuántos clientes")
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, "no parse para 'cuántos clientes'"

    pruned = prune_by_typing(trees, lex)
    assert pruned == trees


def test_juan_ambiguity_pruned_by_table_context(lex):
    iso_lex = Lexicon(
        tables={
            "productos": ["id", "nombre", "categoria", "precio"],
            "vendedores": ["id", "nombre", "ciudad"],
            "clientes": ["id", "nombre", "ciudad"],
        },
        fks={},
        values={},
        values_by_table={},
    )

    juan_vendedor = LexicalItem("VALOR_NOMBRE", "Juan", bindings=[("vendedores", "nombre")])
    juan_cliente = LexicalItem("VALOR_NOMBRE", "Juan", bindings=[("clientes", "nombre")])
    juan_producto_unreal = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[("productos", "nombre")]
    )

    sn_clientes = _sn_tree("clientes")

    tree_a = ParseTree("S", [ParseTree("Pregunta", [sn_clientes, juan_cliente])])
    tree_b = ParseTree("S", [ParseTree("Pregunta", [sn_clientes, juan_vendedor])])
    tree_c = ParseTree("S", [ParseTree("Pregunta", [sn_clientes, juan_producto_unreal])])

    pruned = prune_by_typing([tree_a, tree_b, tree_c], iso_lex)
    assert tree_a in pruned
    assert tree_b not in pruned
    assert tree_c not in pruned
    assert len(pruned) == 1


def test_juan_ambiguity_keeps_fk_reachable_binding(lex):
    sn_clientes = _sn_tree("clientes")
    juan_vendedor = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[("vendedores", "nombre")]
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn_clientes, juan_vendedor])])

    pruned = prune_by_typing([tree], lex)
    assert pruned == [tree]



def test_all_incompatible_returns_empty():
    iso_lex = Lexicon(
        tables={
            "productos": ["id", "nombre"],
            "vendedores": ["id", "nombre"],
        },
        fks={},
        values={},
        values_by_table={},
    )
    sn_productos = _sn_tree("productos")
    bad_leaf = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[("vendedores", "nombre")]
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn_productos, bad_leaf])])
    assert prune_by_typing([tree], iso_lex) == []

def test_column_binding_unreachable_pruned():
    iso_lex = Lexicon(
        tables={
            "productos": ["id", "nombre", "precio"],
            "vendedores": ["id", "nombre", "ciudad"],
        },
        fks={},
        values={},
        values_by_table={},
    )
    sn_productos = _sn_tree("productos")
    col_ciudad = LexicalItem(
        "N_COLUMNA", "ciudad", bindings=[("vendedores", "ciudad")]
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn_productos, col_ciudad])])
    assert prune_by_typing([tree], iso_lex) == []


def test_column_binding_with_one_valid_pair_kept():
    iso_lex = Lexicon(
        tables={
            "clientes": ["id", "nombre", "ciudad"],
            "vendedores": ["id", "nombre", "ciudad"],
        },
        fks={},
        values={},
        values_by_table={},
    )
    sn_clientes = _sn_tree("clientes")
    col_ciudad = LexicalItem(
        "N_COLUMNA",
        "ciudad",
        bindings=[("vendedores", "ciudad"), ("clientes", "ciudad")],
    )
    tree = ParseTree("S", [ParseTree("Pregunta", [sn_clientes, col_ciudad])])
    pruned = prune_by_typing([tree], iso_lex)
    assert pruned == [tree]
