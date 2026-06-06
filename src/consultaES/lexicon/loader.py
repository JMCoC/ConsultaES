import re
import sqlite3
from pathlib import Path

_CREATE_RE = re.compile(
    r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
_REF_RE = re.compile(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", re.IGNORECASE)

_SHARED_VALUE_COLS = ["ciudad", "nombre", "categoria", "tipo"]


def parse_schema(schema_path: str):

    text = Path(schema_path).read_text(encoding="utf-8")
    tables: dict[str, list[str]] = {}
    fks: dict[tuple[str, str], tuple[str, str]] = {}

    for m in _CREATE_RE.finditer(text):
        tname = m.group(1)
        body = m.group(2)
        cols: list[str] = []
        for raw_line in body.split(","):
            line = raw_line.strip()
            if not line:
                continue
            head = line.split(None, 1)[0].upper()
            if head in ("PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT"):
                continue
            col_name = line.split(None, 1)[0]
            cols.append(col_name)
            ref = _REF_RE.search(line)
            if ref:
                fks[(tname, col_name)] = (ref.group(1), ref.group(2))
        tables[tname] = cols

    return tables, fks


def load_values(db_path: str, tables: dict[str, list[str]]) -> dict[str, set[str]]:

    values: dict[str, set[str]] = {c: set() for c in _SHARED_VALUE_COLS}
    if not Path(db_path).exists():
        return values
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        for col in _SHARED_VALUE_COLS:
            for tname, cols in tables.items():
                if col in cols:
                    try:
                        cur.execute(f"SELECT DISTINCT {col} FROM {tname}")
                        for (v,) in cur.fetchall():
                            if v is not None:
                                values[col].add(str(v))
                    except sqlite3.Error:
                        pass
    finally:
        con.close()

    return values


def values_by_table(db_path: str, tables: dict[str, list[str]]) -> dict[tuple[str, str], set[str]]:

    out: dict[tuple[str, str], set[str]] = {}
    if not Path(db_path).exists():
        return out
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        for col in _SHARED_VALUE_COLS:
            for tname, cols in tables.items():
                if col in cols:
                    try:
                        cur.execute(f"SELECT DISTINCT {col} FROM {tname}")
                        s: set[str] = set()
                        for (v,) in cur.fetchall():
                            if v is not None:
                                s.add(str(v))
                        out[(tname, col)] = s
                    except sqlite3.Error:
                        pass
    finally:
        con.close()
        
    return out
