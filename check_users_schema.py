import sqlite3
DB_NAME = 'forum.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("PRAGMA table_info(users)")
print("Users Table Columns:")
for row in c.fetchall():
    print(f"  {row[1]} ({row[2]})")
conn.close()
