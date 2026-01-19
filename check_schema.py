import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topics'")
print(c.fetchone()[0])
conn.close()
