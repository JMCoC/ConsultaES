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

    node = ParseTree(earley_item.lhs)
    for (sym, child) in earley_item.children:
        if isinstance(child, tuple):
            pos, alt_index = child
            resolved = items[pos][alt_index]
            node.children.append(resolved)
        else:
            node.children.append(build_tree(child, items))
    return node
