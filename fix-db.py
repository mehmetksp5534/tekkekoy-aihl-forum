import sqlite3

DB_NAME = "forum.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# replies tablosuna attachment sütunu ekle
try:
    c.execute("ALTER TABLE replies ADD COLUMN attachment TEXT")
    print("replies tablosuna attachment sütunu başarıyla eklendi.")
except sqlite3.OperationalError as e:
    print(f"Sütun zaten var veya hata oluştu: {e}")

# topics tablosuna eksik sütunları kontrol et
try:
    c.execute("PRAGMA table_info(topics)")
    columns = c.fetchall()
    print(f"\nTopics tablosu sütunları ({len(columns)} adet):")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Hata: {e}")

conn.commit()
conn.close()
