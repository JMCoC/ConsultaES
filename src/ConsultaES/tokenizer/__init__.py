from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int


def tokenize(texto: str) -> list[Token]:
    raise NotImplementedError
