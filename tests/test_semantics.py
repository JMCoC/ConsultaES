from pathlib import Path

import pytest

from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.semantics import Column, Condition, SQLAst, interpret

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@pytest.fixture(scope="module")
def rig():
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    g = load_grammar(str(RULES_PATH))
    return lex, g


def _interpret(q: str, rig) -> SQLAst:
    lex, g = rig
    tokens = __import__("consultaES.tokenizer", fromlist=["tokenize"]).tokenize(q)
    items = categorize(tokens, lex)
    trees = parse(items, g)
    assert trees, f"no parse for: {q}"
    return interpret(trees[0])

def test_cuantos_clientes(rig):
    ast = _interpret("cuántos clientes", rig)
    assert isinstance(ast, SQLAst)
    assert ast.tables == ["clientes"]
    assert ast.select == [Column(table="clientes", name="*")]
    assert ast.where == []


def test_muestrame_los_clientes(rig):
    ast = _interpret("muéstrame los clientes", rig)
    assert ast.tables == ["clientes"]
    assert ast.select == [Column(table="clientes", name="*")]
    assert ast.where == []


def test_que_productos(rig):
    ast = _interpret("qué productos", rig)
    assert ast.tables == ["productos"]
    assert ast.select == [Column(table="productos", name="*")]


def test_filtro_ciudad(rig):
    ast = _interpret("cuántos clientes con ciudad igual a 'Cali'", rig)
    assert ast.tables == ["clientes"]
    assert len(ast.where) == 1
    conector, cond = ast.where[0]
    assert conector == ""
    assert isinstance(cond, Condition)
    assert cond.col.name == "ciudad"
    assert cond.op == "="
    assert cond.value == "Cali"


def test_filtro_total_mayor(rig):
    ast = _interpret("muéstrame los pedidos con total mayor que 100000", rig)
    assert ast.tables == ["pedidos"]
    assert len(ast.where) == 1
    _, cond = ast.where[0]
    assert cond.op == ">"
    assert cond.value == 100000


def test_dos_filtros_and(rig):
    ast = _interpret(
        "lista los clientes con ciudad igual a 'Bogotá' y con tipo igual a 'premium'",
        rig,
    )
    assert ast.tables == ["clientes"]
    assert len(ast.where) == 2
    con0, cond0 = ast.where[0]
    con1, cond1 = ast.where[1]
    assert con0 == ""
    assert con1 == "AND"
    assert cond0.col.name == "ciudad"
    assert cond1.col.name == "tipo"


def test_tabla_correcta(rig):
    ast = _interpret("lista los pedidos", rig)
    assert ast.tables == ["pedidos"]
    assert ast.select[0].table == "pedidos"


def test_operador_normalizado(rig):
    ast = _interpret("cuántos pedidos con total menor que 50000", rig)
    _, cond = ast.where[0]
    assert cond.op == "<"


def test_cadena_sin_comillas(rig):
    ast = _interpret("cuántos clientes con ciudad igual a 'Cali'", rig)
    _, cond = ast.where[0]
    assert cond.value == "Cali"
    assert "'" not in str(cond.value)


def test_num_es_numerico(rig):
    ast = _interpret("muéstrame los pedidos con total mayor que 100000", rig)
    _, cond = ast.where[0]
    assert isinstance(cond.value, (int, float))


def test_column_table_none_en_condiciones(rig):
    ast = _interpret("cuántos clientes con ciudad igual a 'Cali'", rig)
    _, cond = ast.where[0]
    assert cond.col.table is None


def test_imperativo_con_filtro(rig):
    ast = _interpret("lista los pedidos con total mayor que 0", rig)
    assert ast.tables == ["pedidos"]
    assert len(ast.where) == 1
    _, cond = ast.where[0]
    assert cond.op == ">"
    assert cond.value == 0
