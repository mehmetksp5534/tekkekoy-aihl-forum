import sqlite3
conn = sqlite3.connect("forum.db")
c = conn.cursor()

print("=== TOPICS ===")
for row in c.execute("SELECT * FROM topics"):
    print(row)

print("\n=== REPLIES ===")
for row in c.execute("SELECT * FROM replies"):
    print(row)

conn.close()
