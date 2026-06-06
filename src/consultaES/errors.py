from dataclasses import dataclass, field


@dataclass(frozen=True)
class Error:
    """Error estructurado del pipeline.

    `pos` es una posición entera relativa a la etapa que reporta el error:
    offset de carácter para errores léxicos, índice de token para errores
    sintácticos y 0 cuando la posición no aplica.
    """

    kind: str
    pos: int
    message: str
    suggestions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.pos is None:
            object.__setattr__(self, "pos", 0)
        object.__setattr__(self, "suggestions", tuple(self.suggestions))
