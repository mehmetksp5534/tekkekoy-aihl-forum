import sqlite3
conn = sqlite3.connect("forum.db")
c = conn.cursor()
for row in c.execute("SELECT * FROM users"):
    print(row)
conn.close()
print("Kullanıcılar listelendi.")