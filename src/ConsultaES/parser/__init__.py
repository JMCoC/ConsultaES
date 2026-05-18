from .earley import earley_parse
from .tree import ParseTree, build_tree

__all__ = ["parse", "ParseTree", "earley_parse", "build_tree"]


def parse(items, grammar) -> list[ParseTree]:
    return [build_tree(it, items) for it in earley_parse(items, grammar)]
