import sqlite3
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute("SELECT id, name, xp FROM users WHERE id=4")
user = c.fetchone()
print(f"User 4: {user}")
c.execute("SELECT COUNT(*) FROM topics")
topics = c.fetchone()[0]
print(f"Topics: {topics}")
conn.close()
