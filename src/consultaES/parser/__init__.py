from consultaES.errors import Error

from .earley import earley_chart, earley_parse
from .tree import ParseTree, build_tree

__all__ = ["parse", "parse_or_error", "ParseTree", "earley_parse", "build_tree"]


def parse(items: list[list], grammar) -> list[ParseTree]:
    return [build_tree(it, items) for it in earley_parse(items, grammar)]


def parse_or_error(items: list[list], grammar) -> list[ParseTree] | Error:
    chart = earley_chart(items, grammar)
    n = len(items)
    completed = [
        it
        for it in chart[n]
        if it.lhs == grammar.start and it.dot == len(it.rhs) and it.origin == 0
    ]
    if completed:
        return [build_tree(it, items) for it in completed]

    active_positions = [i for i, state in enumerate(chart) if state]
    pos = active_positions[-1] if active_positions else 0
    expected = sorted(
        {
            item.rhs[item.dot]
            for item in chart[pos]
            if item.dot < len(item.rhs)
        }
    )
    if not expected:
        expected = sorted(grammar.terminals)
    esperado = ", ".join(expected)
    return Error(
        kind="sintáctico",
        pos=pos,
        message=(
            f"No se pudo completar el análisis sintáctico en la posición {pos}. "
            f"Se esperaba: {esperado}."
        ),
        suggestions=expected,
    )
