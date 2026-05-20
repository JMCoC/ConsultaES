from dataclasses import dataclass, field


@dataclass
class ParseTree:
    label: str
    children: list = field(default_factory=list)  # list[ParseTree | LexicalItem]

    def pretty(self, indent: int = 0) -> str:
        lines = ["  " * indent + self.label]
        for c in self.children:
            if isinstance(c, ParseTree):
                lines.append(c.pretty(indent + 1))
            else:
                lines.append("  " * (indent + 1) + f"[{c.category}:{c.lemma}]")
        return "\n".join(lines)


def build_tree(earley_item, items) -> ParseTree:
    """Build a ParseTree from a completed EarleyItem.

    Terminal children are stored as input indices in `earley_item.children`
    and resolved against `items` (a lattice: list[list[LexicalItem]]) here
    to recover the original LexicalItem.
    """
    node = ParseTree(earley_item.lhs)
    for (sym, child) in earley_item.children:
        if isinstance(child, int):
            # Scanned terminal: resolve index into the lattice.
            # Pick the first alternative whose category matches sym.
            alts = items[child]
            resolved = next((a for a in alts if a.category == sym), alts[0])
            node.children.append(resolved)
        else:
            # Completed non-terminal: recurse.
            node.children.append(build_tree(child, items))
    return node
