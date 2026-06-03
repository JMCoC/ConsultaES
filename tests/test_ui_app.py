from pathlib import Path

from consultaES.disambiguator import Context, DisambiguationOption, DisambiguationRequest
from consultaES.errors import Error
from consultaES.parser.tree import ParseTree
from consultaES.lexicon import LexicalItem
from consultaES.ui import app
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
    assert resultado.columns


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


def test_render_desambiguacion_guarda_error_sin_marcarlo_como_resultado(monkeypatch):
    class FakeStreamlit:
        def __init__(self):
            self.session_state = {}

        def radio(self, _question, *, options, format_func):
            format_func(next(iter(options)))
            return 0

        def button(self, _label):
            return True

        def rerun(self):
            self.session_state["rerun"] = True

    fake_st = FakeStreamlit()
    error = Error(
        kind="ejecución",
        pos=None,
        message="Error SQLite al ejecutar SQL",
        suggestions=["SELECT * FROM tabla_inexistente"],
    )
    tree = ParseTree("S", [LexicalItem("N_TABLA", "tabla_inexistente")])
    solicitud = DisambiguationRequest(
        options=[DisambiguationOption(tree=tree, paraphrase="opción inválida", score=0)]
    )

    monkeypatch.setattr(app, "st", fake_st)
    monkeypatch.setattr(app, "_contexto_sesion", lambda: Context())
    monkeypatch.setattr(app, "resolver_consulta_con_arbol", lambda *_args, **_kwargs: error)

    app._render_desambiguacion(solicitud)

    assert fake_st.session_state["error"] == error
    assert "resultado" not in fake_st.session_state
    assert "solicitud" not in fake_st.session_state
    assert fake_st.session_state["rerun"] is True


def test_main_guarda_error_directo_de_consultar_y_limpia_estado(monkeypatch):
    class FakeStreamlit:
        def __init__(self):
            self.session_state = {
                "resultado": object(),
                "solicitud": object(),
            }
            self.errors = []

        def set_page_config(self, **_kwargs):
            pass

        def title(self, _text):
            pass

        def text_input(self, _label, key):
            self.session_state[key] = "clientess"
            return "clientess"

        def button(self, label):
            return label == "Consultar"

        def error(self, message):
            self.errors.append(message)

        def caption(self, _text):
            pass

    fake_st = FakeStreamlit()
    error = Error(
        kind="léxico",
        pos=0,
        message="No reconozco 'clientess'.",
        suggestions=["clientes"],
    )

    monkeypatch.setattr(app, "st", fake_st)
    monkeypatch.setattr(app, "_contexto_sesion", lambda: Context())
    monkeypatch.setattr(app, "ejecutar_consulta", lambda *_args, **_kwargs: error)

    app.main()

    assert fake_st.session_state["error"] == error
    assert "resultado" not in fake_st.session_state
    assert "solicitud" not in fake_st.session_state
    assert fake_st.errors == [error.message]


def test_render_resultado_muestra_filas_con_nombres_de_columnas(monkeypatch):
    class FakeColumn:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class FakeStreamlit:
        def __init__(self):
            self.dataframes = []

        def columns(self, count):
            return [FakeColumn() for _ in range(count)]

        def subheader(self, _text):
            pass

        def text(self, _text):
            pass

        def code(self, _text, language):
            pass

        def dataframe(self, data):
            self.dataframes.append(data)

    fake_st = FakeStreamlit()
    resultado = app.ResultadoConsulta(
        tree=ParseTree("S", []),
        sql="SELECT id, nombre FROM clientes",
        rows=[(1, "Laura"), (2, "Carlos")],
        columns=["id", "nombre"],
    )

    monkeypatch.setattr(app, "st", fake_st)

    app._render_resultado(resultado)

    assert fake_st.dataframes == [[{"id": 1, "nombre": "Laura"}, {"id": 2, "nombre": "Carlos"}]]
