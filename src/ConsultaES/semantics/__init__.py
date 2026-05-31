from consultaES.lexicon import Lexicon

from .ast import Column, Condition, Join, SQLAst
from .dcg import interpret, interpret_or_error
from .joins import resolve_joins


def prepare_sql_ast(ast: SQLAst, lexicon: Lexicon) -> SQLAst:
    """Aplica pasos semánticos finales antes de generar SQL."""
    return resolve_joins(ast, lexicon)


__all__ = [
    "Column",
    "Condition",
    "Join",
    "SQLAst",
    "interpret",
    "interpret_or_error",
    "prepare_sql_ast",
    "resolve_joins",
]
