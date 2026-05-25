from __future__ import annotations

from collections import deque

from consultaES.lexicon import LexicalItem, Lexicon
from consultaES.parser.tree import ParseTree


_VALUE_CATEGORIES = {"VALOR_NOMBRE", "VALOR_CIUDAD", "VALOR_CATEGORIA", "VALOR_TIPO"}

def _build_fk_adjacency(
    fks: dict[tuple[str, str], tuple[str, str]],
) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {}
    for (src_t, _src_c), (dst_t, _dst_c) in fks.items():
        adj.setdefault(src_t, set()).add(dst_t)
        adj.setdefault(dst_t, set()).add(src_t)
    return adj


def _reachable_tables(start: str, adj: dict[str, set[str]]) -> set[str]:
    visited: set[str] = {start}
    queue: deque[str] = deque([start])
    while queue:
        cur = queue.popleft()
        for nb in adj.get(cur, ()):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return visited


def _collect_sn_tables(node) -> list[str]:
    tables: list[str] = []
    _walk_collect(node, tables)
    return tables


def _walk_collect(node, out: list[str]) -> None:
    if isinstance(node, LexicalItem):
        if node.category == "N_TABLA":
            if node.bindings:
                out.append(node.bindings[0][0])
            else:
                out.append(node.lemma)
        return
    if isinstance(node, ParseTree):
        for c in node.children:
            _walk_collect(c, out)


def _collect_leaves(node) -> list[LexicalItem]:
    leaves: list[LexicalItem] = []
    _walk_leaves(node, leaves)
    return leaves


def _walk_leaves(node, out: list[LexicalItem]) -> None:
    if isinstance(node, LexicalItem):
        out.append(node)
        return
    if isinstance(node, ParseTree):
        for c in node.children:
            _walk_leaves(c, out)

def _tree_is_well_typed(
    tree: ParseTree,
    adj: dict[str, set[str]],
) -> bool:
    sn_tables = _collect_sn_tables(tree)
    if not sn_tables:
        return True

    admissible: set[str] = set()
    for t in sn_tables:
        admissible |= _reachable_tables(t, adj)

    for leaf in _collect_leaves(tree):
        cat = leaf.category
        if cat in _VALUE_CATEGORIES:
            if not leaf.bindings:
                continue
            if not any(t in admissible for (t, _c) in leaf.bindings):
                return False
        elif cat == "N_COLUMNA":
            if not leaf.bindings:
                continue
            if not any(t in admissible for (t, _c) in leaf.bindings):
                return False
    return True


def prune_by_typing(trees: list[ParseTree], lex: Lexicon) -> list[ParseTree]:
    adj = _build_fk_adjacency(lex.fks)
    return [t for t in trees if _tree_is_well_typed(t, adj)]
