import sqlite3
c = sqlite3.connect('forum.db').cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in c.fetchall():
    print(t[0])
