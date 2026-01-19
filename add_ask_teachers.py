import sqlite3

DB_NAME = "forum.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# ask_teachers kolonu var mı kontrol et
c.execute("PRAGMA table_info(topics)")
columns = [column[1] for column in c.fetchall()]

if 'ask_teachers' not in columns:
    print("ask_teachers kolonu ekleniyor...")
    c.execute("ALTER TABLE topics ADD COLUMN ask_teachers INTEGER DEFAULT 0")
    conn.commit()
    print("✅ ask_teachers kolonu başarıyla eklendi!")
else:
    print("ℹ️ ask_teachers kolonu zaten mevcut")

conn.close()
