import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

print("Eski tablo verisi kaydediliyor...")
c.execute("SELECT * FROM topics")
all_topics = c.fetchall()
print(f"Toplam {len(all_topics)} konu kaydedildi")

print("\nEski tablo siliniyor...")
c.execute("DROP TABLE IF EXISTS topics")

print("Yeni tablo oluşturuluyor...")
c.execute("""
CREATE TABLE topics(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  author TEXT NOT NULL,
  solved INT DEFAULT 0,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  file_path TEXT,
  attachment TEXT,
  is_anonymous INT DEFAULT 0,
  is_approved INTEGER DEFAULT 1
)
""")

print("Eski veriler geri yükleniyor...")
for topic in all_topics:
    # topic[0] (eski id) hariç, geri kalanını ekle
    # Yeni tablo otomatik id atayacak
    c.execute("""
    INSERT INTO topics (title, category, content, author, solved, timestamp, file_path, attachment, is_anonymous, is_approved)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, topic[1:])

conn.commit()
print("✓ Tablo başarıyla yenilendi!")

# Sonuç kontrolü
c.execute("SELECT id, title, is_approved FROM topics WHERE is_approved=0")
pending = c.fetchall()
print(f"\nOnay bekleyen konular ({len(pending)}):")
for row in pending:
    print(f"  {row}")

conn.close()
