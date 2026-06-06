from dataclasses import dataclass, field


@dataclass
class CFG:
    start: str
    nonterminals: set[str] = field(default_factory=set)
    terminals: set[str] = field(default_factory=set)
    productions: set[tuple[str, tuple[str, ...]]] = field(default_factory=set)

    def productions_of(self, nt: str):
        return [p for p in self.productions if p[0] == nt]


def load_grammar(path: str) -> CFG:
    g = CFG(start="")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            lhs, rhs = line.split("->", 1)
            lhs = lhs.strip()
            rhs_syms = tuple(rhs.strip().split())
            if not g.start:
                g.start = lhs
            g.productions.add((lhs, rhs_syms))
            g.nonterminals.add(lhs)
            for s in rhs_syms:
                if s.isupper():
                    g.terminals.add(s)
                else:
                    g.nonterminals.add(s)
    return g
