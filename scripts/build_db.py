import pathlib
import sqlite3

DB = pathlib.Path("data/tienda.db")
DB.unlink(missing_ok=True)
con = sqlite3.connect(DB)
con.executescript(pathlib.Path("data/schema.sql").read_text(encoding="utf-8"))
con.executescript(pathlib.Path("data/seed.sql").read_text(encoding="utf-8"))
con.commit()
con.close()
print(f"Built {DB}")
