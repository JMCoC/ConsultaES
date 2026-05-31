from dataclasses import dataclass, field


@dataclass(frozen=True)
class Error:
    kind: str
    pos: int | None
    message: str
    suggestions: list[str] = field(default_factory=list)

