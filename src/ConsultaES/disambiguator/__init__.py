from dataclasses import dataclass, field

from consultaES.disambiguator.typing import prune_by_typing


@dataclass
class Context:
    bindings: dict = field(default_factory=dict)


@dataclass
class DisambiguationRequest:
    options: list = field(default_factory=list)


def disambiguate(trees, ctx: Context):
    raise NotImplementedError


__all__ = [
    "Context",
    "DisambiguationRequest",
    "disambiguate",
    "prune_by_typing",
]
