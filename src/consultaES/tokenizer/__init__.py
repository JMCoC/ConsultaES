from dataclasses import dataclass

from .patterns import build_all, PRIORITY


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int


_DFAS = None


def _get_dfas():
    global _DFAS
    if _DFAS is None:
        _DFAS = build_all()
    return _DFAS


def tokenize(texto: str) -> list[Token]:
    dfas = _get_dfas()
    priority_idx = {name: i for i, name in enumerate(PRIORITY)}
    tokens: list[Token] = []
    i = 0
    n = len(texto)
    while i < n:
        # skip whitespace
        if texto[i].isspace():
            i += 1
            continue
        best_len = 0
        best_kind: str | None = None
        for kind, dfa in dfas:
            mlen = dfa.longest_match(texto, i)
            if mlen > best_len or (
                mlen == best_len and mlen > 0 and best_kind is not None
                and priority_idx[kind] < priority_idx[best_kind]
            ):
                if mlen > 0:
                    best_len = mlen
                    best_kind = kind
        if best_kind is None or best_len == 0:
            # ERROR: emit single char, advance
            tokens.append(Token(kind="ERROR", value=texto[i], start=i, end=i + 1))
            i += 1
            continue
        tokens.append(
            Token(
                kind=best_kind,
                value=texto[i : i + best_len],
                start=i,
                end=i + best_len,
            )
        )
        i += best_len
    return tokens
