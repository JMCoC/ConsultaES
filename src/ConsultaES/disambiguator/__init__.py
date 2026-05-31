from __future__ import annotations

from dataclasses import dataclass, field

from consultaES.errors import Error
from consultaES.disambiguator.dialog import (
    context_bonus,
    paraphrase,
    record_choice,
)
from consultaES.disambiguator.ranking import score
from consultaES.disambiguator.typing import prune_by_typing
from consultaES.lexicon import Lexicon
from consultaES.parser.tree import ParseTree

_DECISIVE_MARGIN = 2


@dataclass
class Context:
    bindings: dict = field(default_factory=dict)


@dataclass
class DisambiguationOption:
    tree: ParseTree
    paraphrase: str
    score: int

    def __iter__(self):
        yield self.tree
        yield self.score

    def __len__(self) -> int:
        return 2

    def __getitem__(self, idx):
        return (self.tree, self.score)[idx]


@dataclass
class DisambiguationRequest:
    options: list = field(default_factory=list)
    question: str = "¿A cuál de estas interpretaciones te refieres?"


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

    scored = [
        (t, score(t, ctx, lex, db_path=db_path) + context_bonus(t, ctx))
        for t in pruned
    ]
    scored.sort(key=lambda ts: -ts[1])

    top_tree, top_score = scored[0]
    if len(scored) == 1:
        return top_tree

    runner_score = scored[1][1]
    if top_score - runner_score >= _DECISIVE_MARGIN:
        return top_tree

    # Empate (margen < _DECISIVE_MARGIN): construimos opciones con
    # paráfrasis lista para la UI.
    options = [
        DisambiguationOption(tree=t, paraphrase=paraphrase(t), score=s)
        for (t, s) in scored
        if top_score - s < _DECISIVE_MARGIN
    ]
    return DisambiguationRequest(options=options)


def disambiguate_or_error(
    trees: list[ParseTree],
    lex: Lexicon,
    ctx: Context | None = None,
    db_path: str | None = "data/tienda.db",
):
    if not trees:
        return Error(
            kind="semántico",
            pos=0,
            message="No hay árboles de análisis para validar semánticamente.",
            suggestions=[],
        )
    result = disambiguate(trees, lex, ctx, db_path=db_path)
    if result is None:
        return Error(
            kind="semántico",
            pos=0,
            message=(
                "La unificación semántica descartó todas las ramas por "
                "incompatibilidad de tipos con el esquema."
            ),
            suggestions=["Revisa que columnas y valores pertenezcan a tablas relacionadas."],
        )
    return result


__all__ = [
    "Context",
    "DisambiguationOption",
    "DisambiguationRequest",
    "context_bonus",
    "disambiguate",
    "disambiguate_or_error",
    "paraphrase",
    "prune_by_typing",
    "record_choice",
    "score",
]
