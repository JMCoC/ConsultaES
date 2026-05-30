from pathlib import Path

from consultaES.disambiguator import Context, DisambiguationRequest
from consultaES.parser.tree import ParseTree
from consultaES.ui.app import ejecutar_consulta, resolver_consulta_con_arbol


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


def _tiene_binding(node, binding: tuple[str, str]) -> bool:
    if hasattr(node, "bindings"):
        return binding in node.bindings
    if isinstance(node, ParseTree):
        return any(_tiene_binding(child, binding) for child in node.children)
    return False


def test_ejecutar_consulta_devuelve_arbol_sql_y_filas():
    ctx = Context()

    resultado = ejecutar_consulta(
        "cuántos clientes",
        ctx,
        schema_path=str(SCHEMA_PATH),
        db_path=str(DB_PATH),
        rules_path=str(RULES_PATH),
    )

    assert not isinstance(resultado, DisambiguationRequest)
    assert resultado.tree.pretty().startswith("S")
    assert "FROM clientes" in resultado.sql
    assert resultado.rows


def test_resolver_consulta_con_arbol_registra_eleccion_y_continua_pipeline():
    ctx = Context()
    solicitud = ejecutar_consulta(
        "ventas de Juan",
        ctx,
        schema_path=str(SCHEMA_PATH),
        db_path=str(DB_PATH),
        rules_path=str(RULES_PATH),
    )
    assert isinstance(solicitud, DisambiguationRequest)

    opcion = next(opt for opt in solicitud.options if _tiene_binding(opt.tree, ("clientes", "nombre")))

    resultado = resolver_consulta_con_arbol(
        opcion.tree,
        ctx,
        schema_path=str(SCHEMA_PATH),
        db_path=str(DB_PATH),
    )

    assert ctx.bindings.get("Juan") == ("clientes", "nombre")
    assert "JOIN clientes" in resultado.sql
    assert resultado.rows
