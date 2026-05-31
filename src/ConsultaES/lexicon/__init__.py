from dataclasses import dataclass, field

from consultaES.errors import Error


@dataclass
class Lexicon:
    tables: dict[str, list[str]] = field(default_factory=dict)
    fks: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)
    values: dict[str, set[str]] = field(default_factory=dict)
    values_by_table: dict[tuple[str, str], set[str]] = field(default_factory=dict)

    def columns_of(self, table: str) -> list[str]:
        return self.tables[table]


@dataclass
class LexicalItem:
    category: str
    lemma: str
    bindings: list = field(default_factory=list)


_INTERROG = {"qué", "cuántos", "cuántas", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo"}
_IMPERATIVO = {"muéstrame", "muestra", "lista", "dame", "dime", "enseña", "enseñame"}
_AGG = {"total", "suma", "promedio", "media", "cuenta", "máximo", "mínimo", "cantidad"}
_PREP = {"de", "en", "con", "por", "para", "desde", "hasta", "sobre"}
_DET = {"el", "la", "los", "las", "un", "una", "unos", "unas"}
_AGR_MARKER = {"agrupados", "agrupado", "agrupadas", "agrupada"}
_ORD_MARKER = {"ordenados", "ordenado", "ordenadas", "ordenada"}
_DIR = {"ascendente", "descendente", "ascendentemente", "descendentemente"}

_SINGULAR_TO_TABLE = {
    "venta": "pedidos",
    "ventas": "pedidos",
    "cliente": "clientes",
    "vendedor": "vendedores",
    "producto": "productos",
    "pedido": "pedidos",
    "detalle": "detalle_pedidos",
}

_VALUE_COL_CATEGORY = {
    "ciudad": "VALOR_CIUDAD",
    "nombre": "VALOR_NOMBRE",
    "categoria": "VALOR_CATEGORIA",
    "tipo": "VALOR_TIPO",
}

_PASSTHROUGH = {"NUM", "CADENA", "FECHA", "OP_COMP", "CONECTOR", "PUNT", "ERROR"}


def levenshtein(a: str, b: str) -> int:
    a = a.lower()
    b = b.lower()
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


def _vocabulario(lex: Lexicon) -> set[str]:
    vocab = set(_INTERROG | _IMPERATIVO | _AGG | _PREP | _DET | _AGR_MARKER | _ORD_MARKER | _DIR)
    vocab.update(_SINGULAR_TO_TABLE)
    vocab.update(lex.tables)
    for cols in lex.tables.values():
        vocab.update(cols)
    for values in lex.values.values():
        vocab.update(str(value).lower() for value in values)
    return vocab


def suggest(word: str, lex: Lexicon, k: int = 3) -> list[str]:
    vocab = sorted(_vocabulario(lex))
    return sorted(vocab, key=lambda candidate: (levenshtein(word, candidate), candidate))[:k]


def validate_lexical_items(tokens, lex: Lexicon) -> Error | None:
    for tok in tokens:
        if tok.kind == "ERROR":
            return Error(
                kind="léxico",
                pos=tok.start,
                message=f"Token no reconocido '{tok.value}' en la posición {tok.start}.",
                suggestions=suggest(tok.value, lex, k=1),
            )
        if tok.kind != "PALABRA":
            continue
        low = tok.value.lower()
        if low not in _vocabulario(lex):
            return Error(
                kind="léxico",
                pos=tok.start,
                message=(
                    f"No reconozco '{tok.value}' en la posición {tok.start}. "
                    "Revisa la palabra o usa un término del esquema."
                ),
                suggestions=suggest(tok.value, lex),
            )
    return None


def build_lexicon(schema_path: str, db_path: str = "data/tienda.db") -> Lexicon:
    from .loader import parse_schema, load_values, values_by_table

    tables, fks = parse_schema(schema_path)
    values = load_values(db_path, tables)
    vbt = values_by_table(db_path, tables)
    lex = Lexicon(tables=tables, fks=fks, values=values, values_by_table=vbt)
    return lex


def _column_index(lex: Lexicon) -> dict[str, list[tuple[str, str]]]:
    idx: dict[str, list[tuple[str, str]]] = {}
    for t, cols in lex.tables.items():
        for c in cols:
            idx.setdefault(c, []).append((t, c))
    return idx


def categorize(tokens, lex: Lexicon) -> list[list[LexicalItem]]:
    lattice: list[list[LexicalItem]] = []
    col_idx = _column_index(lex)

    for tok in tokens:
        kind = tok.kind
        val = tok.value
        low = val.lower()
        alts: list[LexicalItem] = []

        if kind in _PASSTHROUGH:
            alts.append(LexicalItem(category=kind, lemma=val, bindings=[]))
            lattice.append(alts)
            continue

        if kind == "PALABRA":
            if low in _INTERROG:
                alts.append(LexicalItem("INTERROG", val))
            elif low in _IMPERATIVO:
                alts.append(LexicalItem("IMPERATIVO", val))
            elif low in _AGG:
                alts.append(LexicalItem("AGG", val))
            elif low in _AGR_MARKER:
                alts.append(LexicalItem("AGR_MARKER", val))
            elif low in _ORD_MARKER:
                alts.append(LexicalItem("ORD_MARKER", val))
            elif low in _DIR:
                alts.append(LexicalItem("DIR", val))
            elif low in _PREP:
                alts.append(LexicalItem("PREP", val))
            elif low in _DET:
                alts.append(LexicalItem("DET", val))

            table_lemma = None
            if low in lex.tables:
                table_lemma = low
            elif low in _SINGULAR_TO_TABLE and _SINGULAR_TO_TABLE[low] in lex.tables:
                table_lemma = _SINGULAR_TO_TABLE[low]
            if table_lemma is not None:
                alts.append(
                    LexicalItem("N_TABLA", table_lemma, bindings=[(table_lemma, None)])
                )

            if low in col_idx:
                alts.append(
                    LexicalItem("N_COLUMNA", low, bindings=list(col_idx[low]))
                )

            vbt = lex.values_by_table
            for (tname, cname), vset in vbt.items():
                if cname not in _VALUE_COL_CATEGORY:
                    continue
                for v in vset:
                    if v.lower() == low:
                        alts.append(
                            LexicalItem(
                                _VALUE_COL_CATEGORY[cname],
                                v,
                                bindings=[(tname, cname)],
                            )
                        )
                        break

            if not alts:
                alts.append(LexicalItem("PALABRA", val, bindings=[]))
            lattice.append(alts)
            continue

        alts.append(LexicalItem(kind, val, bindings=[]))
        lattice.append(alts)

    return lattice
