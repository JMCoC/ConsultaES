from dataclasses import dataclass, field


@dataclass
class ParseTree:
    label: str
    children: list = field(default_factory=list)


def parse(items, grammar) -> list[ParseTree]:
    raise NotImplementedError
