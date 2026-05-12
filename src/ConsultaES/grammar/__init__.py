from dataclasses import dataclass, field


@dataclass
class CFG:
    start: str
    nonterminals: set[str] = field(default_factory=set)
    terminals: set[str] = field(default_factory=set)
    productions: set = field(default_factory=set)

    def productions_of(self, nt: str):
        return [p for p in self.productions if p[0] == nt]


def load_grammar(path: str) -> CFG:
    raise NotImplementedError
