from dataclasses import dataclass


@dataclass(frozen=True)
class EarleyItem:

    lhs: str
    rhs: tuple[str, ...]
    dot: int
    origin: int
    children: tuple = ()


def earley_parse(items, grammar):

    chart = earley_chart(items, grammar)
    n = len(items)
    return [
        it
        for it in chart[n]
        if it.lhs == grammar.start and it.dot == len(it.rhs) and it.origin == 0
    ]


def earley_chart(items, grammar):
    """Construye el chart completo de Earley para parseo o diagnóstico."""
    n = len(items)
    chart: list[set[EarleyItem]] = [set() for _ in range(n + 1)]

    for (lhs, rhs) in grammar.productions_of(grammar.start):
        chart[0].add(EarleyItem(lhs, rhs, 0, 0))

    changed = True
    while changed:
        changed = False
        for i in range(n + 1):
            for item in list(chart[i]):
                if item.dot < len(item.rhs):
                    sym = item.rhs[item.dot]
                    if sym in grammar.nonterminals:
                        for (lhs2, rhs2) in grammar.productions_of(sym):
                            new = EarleyItem(lhs2, rhs2, 0, i)
                            if new not in chart[i]:
                                chart[i].add(new)
                                changed = True
                    elif i < n:
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

    return chart
