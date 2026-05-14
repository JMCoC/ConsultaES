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


# Vocabularies
_INTERROG = {"qué", "cuántos", "cuántas", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo"}
_IMPERATIVO = {"muéstrame", "muestra", "lista", "dame", "dime", "enseña", "enseñame"}
_AGG = {"total", "suma", "promedio", "media", "cuenta", "máximo", "mínimo", "cantidad"}
_PREP = {"de", "en", "con", "por", "para", "desde", "hasta", "sobre"}
_DET = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

# tables
_SINGULAR_TO_TABLE = {
    "cliente": "clientes",
    "vendedor": "vendedores",
    "producto": "productos",
    "pedido": "pedidos",
    "detalle": "detalle_pedidos",
}

# columns
_VALUE_COL_CATEGORY = {
    "ciudad": "VALOR_CIUDAD",
    "nombre": "VALOR_NOMBRE",
    "categoria": "VALOR_CATEGORIA",
    "tipo": "VALOR_TIPO",
}

# token kinds
_PASSTHROUGH = {"NUM", "CADENA", "FECHA", "OP_COMP", "CONECTOR", "PUNT", "ERROR"}


def build_lexicon(schema_path: str, db_path: str = "data/tienda.db") -> Lexicon:
    from .loader import parse_schema, load_values, values_by_table

    tables, fks = parse_schema(schema_path)

    values = load_values(db_path, tables)

    vbt = values_by_table(db_path, tables)

    lex = Lexicon(tables=tables, fks=fks, values=values)
    lex.values_by_table = vbt

    return lex


def _column_index(lex: Lexicon) -> dict[str, list[tuple[str, str]]]:

    idx: dict[str, list[tuple[str, str]]] = {}

    for t, cols in lex.tables.items():
        for c in cols:
            idx.setdefault(c, []).append((t, c))

    return idx


def categorize(tokens, lex: Lexicon) -> list[LexicalItem]:

    items: list[LexicalItem] = []

    col_idx = _column_index(lex)

    for tok in tokens:
        kind = tok.kind
        val = tok.value
        low = val.lower()

        if kind in _PASSTHROUGH:
            items.append(LexicalItem(category=kind, lemma=val, bindings=[]))
            continue

        if kind == "PALABRA":
            produced = False

            if low in _INTERROG:
                items.append(LexicalItem("INTERROG", val))
                produced = True
            elif low in _IMPERATIVO:
                items.append(LexicalItem("IMPERATIVO", val))
                produced = True
            elif low in _AGG:
                items.append(LexicalItem("AGG", val))
                produced = True
            elif low in _PREP:
                items.append(LexicalItem("PREP", val))
                produced = True
            elif low in _DET:
                items.append(LexicalItem("DET", val))
                produced = True

            table_lemma = None
            if low in lex.tables:
                table_lemma = low
            elif low in _SINGULAR_TO_TABLE and _SINGULAR_TO_TABLE[low] in lex.tables:
                table_lemma = _SINGULAR_TO_TABLE[low]
            if table_lemma is not None:
                items.append(
                    LexicalItem("N_TABLA", table_lemma, bindings=[(table_lemma, None)])
                )
                produced = True

            if low in col_idx:
                items.append(
                    LexicalItem("N_COLUMNA", low, bindings=list(col_idx[low]))
                )
                produced = True

            vbt = getattr(lex, "values_by_table", {})
            for (tname, cname), vset in vbt.items():
                if cname not in _VALUE_COL_CATEGORY:
                    continue
                for v in vset:
                    if v.lower() == low:
                        items.append(
                            LexicalItem(
                                _VALUE_COL_CATEGORY[cname],
                                v,
                                bindings=[(tname, cname)],
                            )
                        )
                        produced = True
                        break

            if not produced:
                items.append(LexicalItem("PALABRA", val, bindings=[]))
            continue

        items.append(LexicalItem(kind, val, bindings=[]))

    return items
