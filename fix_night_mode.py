import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

print("BEFORE:")
c.execute("SELECT id, name, color_code FROM background_colors WHERE id = 6")
print(c.fetchone())

c.execute("UPDATE background_colors SET color_code = '#232323' WHERE id = 6")
conn.commit()

print("\nAFTER:")
c.execute("SELECT id, name, color_code FROM background_colors WHERE id = 6")
print(c.fetchone())

conn.close()
