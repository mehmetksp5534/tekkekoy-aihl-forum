import sqlite3

DB_NAME = "forum.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

print("Veritabanı düzeltiliyor...")

# Eski is_approved sütunu sil (DEFAULT yanlış olduğu için)
try:
    # SQLite'da sütun silme için table'ı yeniden oluşturmak gerekir
    c.execute("""
        CREATE TABLE topics_new AS
        SELECT id, title, category, content, author, solved, timestamp, file_path, attachment, is_anonymous
        FROM topics
    """)
    c.execute("DROP TABLE topics")
    c.execute("ALTER TABLE topics_new RENAME TO topics")
    print("✓ Eski is_approved sütunu temizlendi")
except Exception as e:
    print(f"Hata: {e}")

# Yeni is_approved sütunu ekle (DEFAULT 1 ile - normal konular onaylı olsun)
try:
    c.execute("ALTER TABLE topics ADD COLUMN is_approved INTEGER DEFAULT 1")
    print("✓ Yeni is_approved sütunu eklendi")
except sqlite3.OperationalError as e:
    print(f"Sütun zaten var: {e}")

# Anonim konuları (is_anonymous=1) is_approved=0 olarak ayarla
try:
    c.execute("UPDATE topics SET is_approved=0 WHERE is_anonymous=1")
    rows = c.rowcount
    print(f"✓ {rows} anonim konu onay beklemeye alındı")
except Exception as e:
    print(f"Hata: {e}")

conn.commit()
conn.close()

print("\nVeritabanı düzeltme tamamlandı!")
