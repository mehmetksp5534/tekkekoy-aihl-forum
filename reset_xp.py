import sqlite3

# XP'yi 0'a sıfırla
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute("UPDATE users SET xp=0 WHERE id=4")
conn.commit()

c.execute("SELECT xp FROM users WHERE id=4")
print(f"XP reset to: {c.fetchone()[0]}")

conn.close()
