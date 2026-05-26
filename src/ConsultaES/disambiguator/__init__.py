from __future__ import annotations

from dataclasses import dataclass, field

from consultaES.disambiguator.ranking import score
from consultaES.disambiguator.typing import prune_by_typing
from consultaES.lexicon import Lexicon
from consultaES.parser.tree import ParseTree

_DECISIVE_MARGIN = 2

@dataclass
class Context:
    bindings: dict = field(default_factory=dict)


@dataclass
class DisambiguationRequest:
    options: list = field(default_factory=list)


def disambiguate(
    trees: list[ParseTree],
    lex: Lexicon,
    ctx: Context | None = None,
    db_path: str | None = "data/tienda.db",
):
    if not trees:
        return None

    pruned = prune_by_typing(trees, lex)
    if not pruned:
        return None
    if len(pruned) == 1:
        return pruned[0]

    scored = [(t, score(t, ctx, lex, db_path=db_path)) for t in pruned]
    scored.sort(key=lambda ts: -ts[1])

    top_tree, top_score = scored[0]
    if len(scored) == 1:
        return top_tree

    runner_score = scored[1][1]
    if top_score - runner_score >= _DECISIVE_MARGIN:
        return top_tree

    options = [(t, s) for (t, s) in scored if top_score - s < _DECISIVE_MARGIN]
    return DisambiguationRequest(options=options)


__all__ = [
    "Context",
    "DisambiguationRequest",
    "disambiguate",
    "prune_by_typing",
    "score",
]
