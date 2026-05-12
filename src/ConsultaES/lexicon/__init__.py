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


def build_lexicon(schema_path: str, db_path: str = "data/tienda.db") -> Lexicon:
    raise NotImplementedError


def categorize(tokens, lex: Lexicon) -> list[LexicalItem]:
    raise NotImplementedError
