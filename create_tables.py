import sqlite3

DB_NAME = "forum.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

try:
    c.execute("ALTER TABLE topics ADD COLUMN attachment TEXT")
    print("Attachment sütunu başarıyla eklendi.")
except Exception as e:
    print("Zaten ekli olabilir veya başka bir hata oluştu:")
    print(e)

conn.commit()
conn.close()
