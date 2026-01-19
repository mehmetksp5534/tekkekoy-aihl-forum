import sqlite3

# forum.db adında bir veritabanı oluşturuyor
conn = sqlite3.connect("forum.db")
c = conn.cursor()

# users tablosunu oluşturuyor
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database ve users tablosu oluşturuldu!")
