import sqlite3

DB_NAME = "forum.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Users tablosu sütunlarını kontrol et
c.execute("PRAGMA table_info(users)")
columns = c.fetchall()
print("Users tablosu sütunları:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Yeni sütunları ekle
try:
    c.execute("ALTER TABLE users ADD COLUMN bio TEXT")
    print("\n✓ bio sütunu eklendi")
except sqlite3.OperationalError:
    print("\n✗ bio sütunu zaten var")

try:
    c.execute("ALTER TABLE users ADD COLUMN profile_photo TEXT")
    print("✓ profile_photo sütunu eklendi")
except sqlite3.OperationalError:
    print("✗ profile_photo sütunu zaten var")

conn.commit()
conn.close()
print("\nVeritabanı güncelleme tamamlandı!")
