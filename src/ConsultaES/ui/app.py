from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from consultaES.disambiguator import (
    Context,
    DisambiguationRequest,
    disambiguate,
    record_choice,
)
from consultaES.grammar import load_grammar
from consultaES.lexicon import build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.semantics import interpret, prepare_sql_ast
from consultaES.sqlgen import generate
from consultaES.tokenizer import tokenize

try:
    import streamlit as st
except ImportError: 
    st = None


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


@dataclass
class ResultadoConsulta:
    tree: ParseTree
    sql: str
    rows: list


def resolver_consulta_con_arbol(
    tree: ParseTree,
    ctx: Context,
    *,
    schema_path: str = str(SCHEMA_PATH),
    db_path: str = str(DB_PATH),
) -> ResultadoConsulta:
    """Continúa el pipeline desde un árbol ya elegido."""
    lex = build_lexicon(schema_path, db_path)
    record_choice(ctx, tree)
    ast = prepare_sql_ast(interpret(tree), lex)
    sql, rows = generate(ast, db=db_path, execute=True)
    return ResultadoConsulta(tree=tree, sql=sql, rows=rows)


def ejecutar_consulta(
    texto: str,
    ctx: Context,
    *,
    schema_path: str = str(SCHEMA_PATH),
    db_path: str = str(DB_PATH),
    rules_path: str = str(RULES_PATH),
) -> ResultadoConsulta | DisambiguationRequest:
    """Ejecuta tokenizer -> lexicon -> parser -> disambiguator -> semantics -> sqlgen."""
    lex = build_lexicon(schema_path, db_path)
    grammar = load_grammar(rules_path)
    tokens = tokenize(texto)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    if not trees:
        raise ValueError("No se pudo construir un árbol de análisis para la consulta.")

    elegido = disambiguate(trees, lex, ctx, db_path=db_path)
    if elegido is None:
        raise ValueError("No se encontró una interpretación semántica válida.")
    if isinstance(elegido, DisambiguationRequest):
        return elegido
    return resolver_consulta_con_arbol(elegido, ctx, schema_path=schema_path, db_path=db_path)


def _contexto_sesion() -> Context:
    if "context" not in st.session_state:
        st.session_state["context"] = Context()
    return st.session_state["context"]


def _render_resultado(resultado: ResultadoConsulta) -> None:
    col_arbol, col_sql, col_resultados = st.columns(3)
    with col_arbol:
        st.subheader("Arbol")
        st.text(resultado.tree.pretty())
    with col_sql:
        st.subheader("SQL")
        st.code(resultado.sql, language="sql")
    with col_resultados:
        st.subheader("Resultados")
        st.dataframe(resultado.rows)


def _render_desambiguacion(solicitud: DisambiguationRequest) -> None:
    opciones = list(solicitud.options)
    seleccion = st.radio(
        solicitud.question,
        options=range(len(opciones)),
        format_func=lambda idx: opciones[idx].paraphrase,
    )
    if st.button("Confirmar interpretación"):
        ctx = _contexto_sesion()
        resultado = resolver_consulta_con_arbol(opciones[seleccion].tree, ctx)
        st.session_state["resultado"] = resultado
        st.session_state.pop("solicitud", None)
        st.rerun()


def main() -> None:
    if st is None:
        raise RuntimeError("Streamlit no está instalado.")

    st.set_page_config(page_title="ConsultaES", layout="wide")
    st.title("ConsultaES")

    ctx = _contexto_sesion()
    texto = st.text_input("Consulta", key="consulta")

    if st.button("Consultar"):
        st.session_state.pop("resultado", None)
        st.session_state.pop("solicitud", None)
        try:
            salida = ejecutar_consulta(texto, ctx)
        except ValueError as exc:
            st.error(str(exc))
        else:
            if isinstance(salida, DisambiguationRequest):
                st.session_state["solicitud"] = salida
            else:
                st.session_state["resultado"] = salida

    solicitud = st.session_state.get("solicitud")
    if solicitud is not None:
        _render_desambiguacion(solicitud)

    resultado = st.session_state.get("resultado")
    if resultado is not None:
        _render_resultado(resultado)


if __name__ == "__main__":
    main()
