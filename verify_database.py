"""
Çerçeve, rozet ve renk seçiminin doğru kaydedildiğini kontrol et
"""
import sqlite3

DB_NAME = 'forum.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

print("=" * 70)
print("VERİTABANI KONTROL")
print("=" * 70)

# Testuser'ın seçimlerini kontrol et
c.execute("""
    SELECT id, username, xp, selected_frame_id, selected_badge_id, selected_bg_color_id
    FROM users WHERE username='testuser'
""")
user = c.fetchone()

if user:
    print(f"\nTest User: {user[1]}")
    print(f"  XP: {user[2]}")
    print(f"  Seçili Çerçeve ID: {user[3]}")
    print(f"  Seçili Rozet ID: {user[4]}")
    print(f"  Seçili Renk ID: {user[5]}")
    
    # Frame detaylarını al
    if user[3]:
        c.execute("SELECT name, color FROM frames WHERE id=?", (user[3],))
        frame = c.fetchone()
        if frame:
            print(f"\n  → Çerçeve: {frame[0]} (Renk: {frame[1]})")
    
    # Badge detaylarını al
    if user[4]:
        c.execute("SELECT name, icon_path FROM badges WHERE id=?", (user[4],))
        badge = c.fetchone()
        if badge:
            print(f"  → Rozet: {badge[0]} (İkon: {badge[1]})")
    
    # Color detaylarını al
    if user[5]:
        c.execute("SELECT name, color_code, gradient_code FROM bg_colors WHERE id=?", (user[5],))
        color = c.fetchone()
        if color:
            bg = color[2] if color[2] else color[1]
            print(f"  → Arka Plan: {color[0]} (Stil: {bg[:50]}...)")

# Tüm çerçeveleri kontrol et
print("\n" + "=" * 70)
print("ÇERÇEVELER")
print("=" * 70)
c.execute("SELECT COUNT(*) FROM frames")
print(f"\nToplam: {c.fetchone()[0]} çerçeve")
c.execute("SELECT id, name FROM frames")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Tüm rozetleri kontrol et
print("\n" + "=" * 70)
print("ROZETLER")
print("=" * 70)
c.execute("SELECT COUNT(*) FROM badges")
print(f"\nToplam: {c.fetchone()[0]} rozet")
c.execute("SELECT id, name, required_xp FROM badges ORDER BY required_xp")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} (Gerekli XP: {row[2]})")

# Tüm renkleri kontrol et
print("\n" + "=" * 70)
print("RENKLER")
print("=" * 70)
c.execute("SELECT COUNT(*) FROM bg_colors")
print(f"\nToplam: {c.fetchone()[0]} renk")
c.execute("SELECT id, name FROM bg_colors")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()

print("\n" + "=" * 70)
print("✅ VERİTABANI DOĞRULMASI TAMAMLANDI")
print("=" * 70)
