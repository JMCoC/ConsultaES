from dataclasses import dataclass, field


@dataclass
class Lexicon:
    tables: dict[str, list[str]] = field(default_factory=dict)
    fks: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)
    values: dict[str, set[str]] = field(default_factory=dict)

    def columns_of(self, table: str) -> list[str]:
        return self.tables[table]


@dataclass
class LexicalItem:
    category: str
    lemma: str
    bindings: list = field(default_factory=list)


# Closed-class vocabularies.
_INTERROG = {"qué", "cuántos", "cuántas", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo"}
_IMPERATIVO = {"muéstrame", "muestra", "lista", "dame", "dime", "enseña", "enseñame"}
_AGG = {"total", "suma", "promedio", "media", "cuenta", "máximo", "mínimo", "cantidad"}
_PREP = {"de", "en", "con", "por", "para", "desde", "hasta", "sobre"}
_DET = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

# singular -> table lemma
_SINGULAR_TO_TABLE = {
    "cliente": "clientes",
    "vendedor": "vendedores",
    "producto": "productos",
    "pedido": "pedidos",
    "detalle": "detalle_pedidos",
}

# shared value column -> category suffix
_VALUE_COL_CATEGORY = {
    "ciudad": "VALOR_CIUDAD",
    "nombre": "VALOR_NOMBRE",
    "categoria": "VALOR_CATEGORIA",
    "tipo": "VALOR_TIPO",
}

# Token kinds that pass through as categories directly.
_PASSTHROUGH = {"NUM", "CADENA", "FECHA", "OP_COMP", "CONECTOR", "PUNT", "ERROR"}


def build_lexicon(schema_path: str, db_path: str = "data/tienda.db") -> Lexicon:
    from .loader import parse_schema, load_values, values_by_table

    tables, fks = parse_schema(schema_path)
    values = load_values(db_path, tables)
    vbt = values_by_table(db_path, tables)
    lex = Lexicon(tables=tables, fks=fks, values=values)
    # Stash per-(table, column) values for fine-grained ambiguity resolution.
    lex.values_by_table = vbt  # type: ignore[attr-defined]
    return lex


def _column_index(lex: Lexicon) -> dict[str, list[tuple[str, str]]]:
    """Column name -> list of (table, column) pairs where it appears."""
    idx: dict[str, list[tuple[str, str]]] = {}
    for t, cols in lex.tables.items():
        for c in cols:
            idx.setdefault(c, []).append((t, c))
    return idx


def categorize(tokens, lex: Lexicon) -> list[list[LexicalItem]]:
    """Return a lattice: one position per input token, each holding all interpretations."""
    lattice: list[list[LexicalItem]] = []
    col_idx = _column_index(lex)

    for tok in tokens:
        kind = tok.kind
        val = tok.value
        low = val.lower()
        alts: list[LexicalItem] = []

        # Pass-through kinds
        if kind in _PASSTHROUGH:
            alts.append(LexicalItem(category=kind, lemma=val, bindings=[]))
            lattice.append(alts)
            continue

        if kind == "PALABRA":
            # Closed classes (check before entity lookups; these are fixed vocab)
            if low in _INTERROG:
                alts.append(LexicalItem("INTERROG", val))
            elif low in _IMPERATIVO:
                alts.append(LexicalItem("IMPERATIVO", val))
            elif low in _AGG:
                alts.append(LexicalItem("AGG", val))
            elif low in _PREP:
                alts.append(LexicalItem("PREP", val))
            elif low in _DET:
                alts.append(LexicalItem("DET", val))

            # N_TABLA: direct table match or singular->plural
            table_lemma = None
            if low in lex.tables:
                table_lemma = low
            elif low in _SINGULAR_TO_TABLE and _SINGULAR_TO_TABLE[low] in lex.tables:
                table_lemma = _SINGULAR_TO_TABLE[low]
            if table_lemma is not None:
                alts.append(
                    LexicalItem("N_TABLA", table_lemma, bindings=[(table_lemma, None)])
                )

            # N_COLUMNA: if lemma is a known column (in any table)
            if low in col_idx:
                alts.append(
                    LexicalItem("N_COLUMNA", low, bindings=list(col_idx[low]))
                )

            # VALOR_<col>: case-insensitive match against seeded values per (table, col)
            vbt = getattr(lex, "values_by_table", {})
            for (tname, cname), vset in vbt.items():
                if cname not in _VALUE_COL_CATEGORY:
                    continue
                # case-insensitive compare
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

        # Unknown kind — pass through
        alts.append(LexicalItem(kind, val, bindings=[]))
        lattice.append(alts)

    return lattice
