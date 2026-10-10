import sqlite3

c = sqlite3.connect("data/database/careerpulse.db")
bad = "\u00e2"  # the broken character in "we\u00e2 re"
rows = c.execute(
    "select source, count(*) from jobs where description like ? group by source",
    (f"%{bad}%",),
).fetchall()
print("jobs with broken text, by source:", rows)