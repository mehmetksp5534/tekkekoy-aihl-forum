import sqlite3

print("🔄 GÜNCELLENECEK:")
print("  ID: 6, Name: 'Gece Modu Koyu'")
print("  Eski renk: #1A1A1A (çok siyah)")
print("  Yeni renk: #333333 (biraz açık gri)")
print()

# Güncelle
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute("UPDATE background_colors SET color_code = ? WHERE id = 6", ("#333333",))
conn.commit()

print("✅ Güncellendi!")
print()

# Kontrol et
c.execute("SELECT id, name, color_code FROM background_colors WHERE id = 6")
row = c.fetchone()
print(f"Doğrulama:")
print(f"  ID: {row[0]}, Name: {row[1]}, Color: {row[2]}")
conn.close()
