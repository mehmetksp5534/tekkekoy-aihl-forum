import sqlite3

DB_NAME = "forum.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# topics tablosuna is_anonymous sütunu ekle
try:
    c.execute("ALTER TABLE topics ADD COLUMN is_anonymous INTEGER DEFAULT 0")
    print("✓ is_anonymous sütunu eklendi")
except sqlite3.OperationalError:
    print("✗ is_anonymous sütunu zaten var")

# topics tablosuna is_approved sütunu ekle
try:
    c.execute("ALTER TABLE topics ADD COLUMN is_approved INTEGER DEFAULT 1")
    print("✓ is_approved sütunu eklendi")
except sqlite3.OperationalError:
    print("✗ is_approved sütunu zaten var")

conn.commit()
conn.close()
print("\nVeritabanı güncelleme tamamlandı!")
