import sqlite3

conn = sqlite3.connect('promptpulse.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)

for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    cnt = c.fetchone()[0]
    print(f"Table {t}: {cnt} rows")
