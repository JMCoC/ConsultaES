from dataclasses import dataclass


@dataclass(frozen=True)
class EarleyItem:
    """A chart item in the Earley parser.

    children is a tuple of (sym, child) pairs where child is either:
      - an EarleyItem (hashable, frozen)   -> completed non-terminal
      - an int (index into the input)      -> scanned terminal
    Using an int for terminals keeps EarleyItem hashable even though
    LexicalItem has a list field (and is therefore unhashable).
    """

    lhs: str
    rhs: tuple[str, ...]
    dot: int
    origin: int
    children: tuple = ()


def earley_parse(items, grammar):
    """Classical Earley chart parser.

    Returns the list of completed items spanning the whole input that
    correspond to the grammar's start symbol.
    """
    n = len(items)
    chart: list[set[EarleyItem]] = [set() for _ in range(n + 1)]

    # Seed chart[0] with all start-symbol productions.
    for (lhs, rhs) in grammar.productions_of(grammar.start):
        chart[0].add(EarleyItem(lhs, rhs, 0, 0))

    changed = True
    # Re-scan fixpoint (not agenda-based). O(n² · |chart|) in practice; acceptable for the small grammars used by ConsultaES.
    while changed:
        changed = False
        for i in range(n + 1):
            for item in list(chart[i]):
                if item.dot < len(item.rhs):
                    sym = item.rhs[item.dot]
                    if sym in grammar.nonterminals:
                        # PREDICT
                        for (lhs2, rhs2) in grammar.productions_of(sym):
                            new = EarleyItem(lhs2, rhs2, 0, i)
                            if new not in chart[i]:
                                chart[i].add(new)
                                changed = True
                    elif i < n:
                        # SCAN: items[i] is a list of alternatives (lattice).
                        for alt_index, alt in enumerate(items[i]):
                            if alt.category == sym:
                                new = EarleyItem(
                                    item.lhs,
                                    item.rhs,
                                    item.dot + 1,
                                    item.origin,
                                    item.children + ((sym, (i, alt_index)),),
                                )
                                if new not in chart[i + 1]:
                                    chart[i + 1].add(new)
                                    changed = True
                else:
                    # COMPLETE
                    for parent in list(chart[item.origin]):
                        if (
                            parent.dot < len(parent.rhs)
                            and parent.rhs[parent.dot] == item.lhs
                        ):
                            new = EarleyItem(
                                parent.lhs,
                                parent.rhs,
                                parent.dot + 1,
                                parent.origin,
                                parent.children + ((item.lhs, item),),
                            )
                            if new not in chart[i]:
                                chart[i].add(new)
                                changed = True

    return [
        it
        for it in chart[n]
        if it.lhs == grammar.start and it.dot == len(it.rhs) and it.origin == 0
    ]
