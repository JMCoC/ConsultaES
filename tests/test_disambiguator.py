from __future__ import annotations

from pathlib import Path

import pytest

from consultaES.disambiguator import (
    Context,
    DisambiguationOption,
    DisambiguationRequest,
    context_bonus,
    disambiguate,
    paraphrase,
    record_choice,
)
from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem, build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.tokenizer import tokenize


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def lex():
    return build_lexicon(str(SCHEMA_PATH), str(DB_PATH))


@pytest.fixture(scope="module")
def grammar():
    return load_grammar(str(RULES_PATH))


def _ventas_de_juan(role_table: str) -> ParseTree:
    """Construye un árbol mínimo con SN=ventas y un VALOR_NOMBRE=Juan
    cuyo binding apunta a (role_table, 'nombre')."""
    sn = ParseTree(
        "SN",
        [LexicalItem("N_TABLA", "ventas", bindings=[("ventas", None)])],
    )
    juan = LexicalItem(
        "VALOR_NOMBRE", "Juan", bindings=[(role_table, "nombre")]
    )
    return ParseTree("S", [ParseTree("Pregunta", [sn, juan])])

def test_paraphrase_basic_query(lex, grammar):
    tokens = tokenize("cuántos clientes")
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees
    out = paraphrase(trees[0])
    assert out, "paráfrasis vacía"
    assert "clientes" in out.lower()
    assert "cuántos" in out.lower()

def test_paraphrase_disambiguates_juan_role():
    t_vend = _ventas_de_juan("vendedores")
    t_cli = _ventas_de_juan("clientes")
    p_vend = paraphrase(t_vend)
    p_cli = paraphrase(t_cli)
    assert p_vend != p_cli
    assert "vendedor" in p_vend.lower()
    assert "cliente" in p_cli.lower()
    # Ambas deben mencionar el lemma original.
    assert "Juan" in p_vend
    assert "Juan" in p_cli

E2E_CORPUS = [
    "cuántos clientes",
    "muéstrame los productos",
    "qué vendedores",
    "lista los pedidos",
    "cuántos clientes con ciudad igual a 'Cali'",
    "muéstrame los pedidos con total mayor que 100000",
    "lista los productos con precio menor que 50000",
    "muéstrame los clientes con tipo igual a 'premium'",
    "cuenta de clientes",
    "suma de total de pedidos",
    "promedio de precio de productos",
    "máximo de total de pedidos",
    "mínimo de total de pedidos",
    "cuántos clientes agrupados por ciudad",
    "cuenta de clientes agrupados por tipo",
    "muéstrame los productos ordenados por precio",
    "muéstrame los productos ordenados por precio descendente",
    "muéstrame los 5 productos",
    "muéstrame los pedidos con total mayor que 100 ordenados por total",
    "cuenta de clientes con tipo igual a 'premium' agrupados por ciudad",
    "muéstrame los 5 productos ordenados por precio descendente",
    "máximo de total de pedidos con total mayor que 100",
]


@pytest.mark.parametrize("query", E2E_CORPUS)
def test_paraphrase_total_over_corpus(query, lex, grammar):
    tokens = tokenize(query)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, f"no parse for: {query}"
    for t in trees:
        out = paraphrase(t)
        assert isinstance(out, str)
        assert out.strip(), f"paráfrasis vacía para: {query}"

def test_disambiguation_request_carries_paraphrases(lex):
    sn = ParseTree(
        "SN",
        [LexicalItem("N_TABLA", "clientes", bindings=[("clientes", None)])],
    )
    val = LexicalItem(
        "VALOR_CIUDAD", "Cali", bindings=[("clientes", "ciudad")]
    )
    f_children = [
        LexicalItem("PREP", "con"),
        LexicalItem("N_COLUMNA", "ciudad", bindings=[("clientes", "ciudad")]),
        LexicalItem("OP_COMP", "igual a"),
        ParseTree("Valor", [val]),
    ]
    f = ParseTree("Filtro", f_children)
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
        assert isinstance(opt, DisambiguationOption)
        assert isinstance(opt.paraphrase, str) and opt.paraphrase.strip()
        # Compatibilidad legacy: desempaque (tree, score).
        tree, score_val = opt
        assert isinstance(tree, ParseTree)
        assert isinstance(score_val, int)

def test_record_choice_persists_bindings():
    ctx = Context()
    tree = _ventas_de_juan("vendedores")
    record_choice(ctx, tree)
    assert ctx.bindings.get("Juan") == ("vendedores", "nombre")

    # Una elección posterior con el mismo lemma debe sobre-escribir.
    tree2 = _ventas_de_juan("clientes")
    record_choice(ctx, tree2)
    assert ctx.bindings.get("Juan") == ("clientes", "nombre")

def test_context_bonus_breaks_tie():
    ctx = Context(bindings={"Juan": ("vendedores", "nombre")})
    t_vend = _ventas_de_juan("vendedores")
    t_cli = _ventas_de_juan("clientes")
    assert context_bonus(t_vend, ctx) >= 1
    assert context_bonus(t_cli, ctx) == 0
    # Diferencia estrictamente positiva por la regla.
    assert context_bonus(t_vend, ctx) > context_bonus(t_cli, ctx)
