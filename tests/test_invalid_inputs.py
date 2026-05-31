from pathlib import Path
import sqlite3

import pytest

from consultaES import sqlgen
from consultaES.disambiguator import Context, disambiguate_or_error
from consultaES.errors import Error
from consultaES.grammar import load_grammar
from consultaES.lexicon import (
    LexicalItem,
    Lexicon,
    build_lexicon,
    categorize,
    validate_lexical_items,
)
from consultaES.parser import parse_or_error
from consultaES.parser.tree import ParseTree
from consultaES.semantics import interpret_or_error
from consultaES.semantics.ast import Column, SQLAst
from consultaES.sqlgen import generate_or_error
from consultaES.tokenizer import tokenize
from consultaES.ui.app import ejecutar_consulta, resolver_consulta_con_arbol

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def rig():
    return build_lexicon(str(SCHEMA_PATH), str(DB_PATH)), load_grammar(str(RULES_PATH))


def _items(texto: str, rig):
    lex, _grammar = rig
    tokens = tokenize(texto)
    err = validate_lexical_items(tokens, lex)
    assert err is None
    return categorize(tokens, lex)


def test_error_lexico_por_token_no_reconocido_sugiere_vocabulario(rig):
    lex, _grammar = rig
    tokens = tokenize("muéstrame @ clientes")

    err = validate_lexical_items(tokens, lex)

    assert err == Error(
        kind="léxico",
        pos=10,
        message="Token no reconocido '@' en la posición 10.",
        suggestions=["de"],
    )


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("clientess", "clientes"),
        ("vendedorez", "vendedores"),
        ("produtos", "productos"),
    ],
)
def test_error_lexico_por_palabra_fuera_del_lexicon_sugiere_por_levenshtein(
    texto, esperado, rig
):
    lex, _grammar = rig
    tokens = tokenize(texto)

    err = validate_lexical_items(tokens, lex)

    assert err is not None
    assert err.kind == "léxico"
    assert err.pos == 0
    assert esperado in err.suggestions
    assert "No reconozco" in err.message


@pytest.mark.parametrize(
    "texto, pos_esperada, simbolo_esperado",
    [
        ("muéstrame con clientes", 1, "SN"),
        ("cuántos clientes con", 3, "N_COLUMNA"),
        ("lista los productos por precio", 5, "OP_COMP"),
    ],
)
def test_error_sintactico_reporta_ultima_posicion_activa_y_esperados(
    texto, pos_esperada, simbolo_esperado, rig
):
    _lex, grammar = rig
    resultado = parse_or_error(_items(texto, rig), grammar)

    assert isinstance(resultado, Error)
    assert resultado.kind == "sintáctico"
    assert resultado.pos == pos_esperada
    assert simbolo_esperado in resultado.suggestions
    assert "Se esperaba" in resultado.message


def test_error_semantico_cuando_tipado_descarta_todas_las_ramas():
    lex = Lexicon(
        tables={
            "productos": ["id", "nombre"],
            "vendedores": ["id", "nombre"],
        },
        fks={},
        values={},
        values_by_table={},
    )
    tree = ParseTree(
        "S",
        [
            ParseTree(
                "Pregunta",
                [
                    LexicalItem("N_TABLA", "productos", bindings=[("productos", None)]),
                    LexicalItem("VALOR_NOMBRE", "Juan", bindings=[("vendedores", "nombre")]),
                ],
            )
        ],
    )

    err = disambiguate_or_error([tree], lex, Context())

    assert isinstance(err, Error)
    assert err.kind == "semántico"
    assert err.pos == 0
    assert "tipos" in err.message


def test_error_semantico_cuando_dcg_no_produce_sql_ast():
    tree = ParseTree("S", [LexicalItem("PALABRA", "nada")])

    err = interpret_or_error(tree)

    assert isinstance(err, Error)
    assert err.kind == "semántico"
    assert "SQLAst" in err.message


def test_error_ejecucion_sqlite_incluye_sql_y_error_sin_lanzar():
    ast = SQLAst(select=[Column(table=None, name="*")], tables=["tabla_inexistente"])

    err = generate_or_error(ast, db=str(DB_PATH), execute=True)

    assert isinstance(err, Error)
    assert err.kind == "ejecución"
    assert err.pos is None
    assert "SELECT * FROM tabla_inexistente" in err.message
    assert "SQLite" in err.message
    assert err.suggestions == ["SELECT * FROM tabla_inexistente"]


def test_error_ejecucion_cierra_conexion_sqlite_si_execute_falla(monkeypatch):
    class FakeConnection:
        def __init__(self):
            self.closed = False

        def execute(self, _sql, _params):
            raise sqlite3.OperationalError("tabla ausente")

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    monkeypatch.setattr(sqlgen.sqlite3, "connect", lambda _db_path: fake_connection)
    ast = SQLAst(select=[Column(table=None, name="*")], tables=["tabla_inexistente"])

    err = generate_or_error(ast, db="fake.db", execute=True)

    assert isinstance(err, Error)
    assert err.kind == "ejecución"
    assert fake_connection.closed is True


def test_ui_devuelve_error_estructurado_para_entrada_lexica_invalida(rig):
    ctx = Context()

    resultado = ejecutar_consulta(
        "clientess",
        ctx,
        schema_path=str(SCHEMA_PATH),
        db_path=str(DB_PATH),
        rules_path=str(RULES_PATH),
    )

    assert isinstance(resultado, Error)
    assert resultado.kind == "léxico"
    assert "clientes" in resultado.suggestions


def test_ui_resolver_arbol_devuelve_error_estructurado_de_ejecucion():
    tree = ParseTree(
        "S",
        [
            ParseTree(
                "Pregunta",
                [
                    ParseTree(
                        "Nucleo",
                        [
                            ParseTree("Interrog", [LexicalItem("INTERROG", "qué")]),
                            ParseTree("SN", [LexicalItem("N_TABLA", "tabla_inexistente")]),
                        ],
                    )
                ],
            )
        ],
    )

    resultado = resolver_consulta_con_arbol(
        tree,
        Context(),
        schema_path=str(SCHEMA_PATH),
        db_path=str(DB_PATH),
    )

    assert isinstance(resultado, Error)
    assert resultado.kind in {"semántico", "ejecución"}
