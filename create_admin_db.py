import sqlite3

conn = sqlite3.connect("forum.db")
c = conn.cursor()

# Admin kullanıcı ekle
c.execute("""
INSERT INTO users (name, email, password, role)
VALUES (?, ?, ?, ?)
""", ("Mehmet Emin Kasap", "mekacreative55@gmail.com", "MeKaC55_", "admin"))

conn.commit()
conn.close()

print("Admin hesabı eklendi!")