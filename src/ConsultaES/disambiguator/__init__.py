from dataclasses import dataclass, field


@dataclass
class Context:
    bindings: dict = field(default_factory=dict)


@dataclass
class DisambiguationRequest:
    options: list = field(default_factory=list)


def disambiguate(trees, ctx: Context):
    raise NotImplementedError
