import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

# Test user varsa ID'sini bul
c.execute("SELECT id FROM users WHERE name='testuser'")
result = c.fetchone()
if result:
    user_id = result[0]
    print(f"Test user zaten var (ID: {user_id})")
else:
    # Yeni user oluştur
    c.execute("INSERT INTO users (name, email, password, role, bio, xp) VALUES (?, ?, ?, ?, ?, ?)",
              ('testuser', 'testuser123@example.com', 'hash', 'user', 'Test', 0))
    conn.commit()
    user_id = c.lastrowid
    print(f"Test user oluşturuldu (ID: {user_id})")

# XP'yi 150 yap
c.execute("UPDATE users SET xp=? WHERE id=?", (150, user_id))
conn.commit()

# Tüm frame ve badge'leri aç
c.execute("SELECT id FROM frames")
for row in c.fetchall():
    c.execute("INSERT OR IGNORE INTO user_frames (user_id, frame_id) VALUES (?, ?)", (user_id, row[0]))

c.execute("SELECT id FROM badges")
for row in c.fetchall():
    c.execute("INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, row[0]))

c.execute("SELECT id FROM background_colors")
for row in c.fetchall():
    # Kullanıcının arka plan rengini direkt seçmek için users tablosunu güncelle
    c.execute("UPDATE users SET selected_bg_color_id=? WHERE id=?", (row[0], user_id))
    break  # Sadece ilki seç

conn.commit()

# Kontrol
c.execute("SELECT COUNT(*) FROM user_frames WHERE user_id=?", (user_id,))
frames = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM user_badges WHERE user_id=?", (user_id,))
badges = c.fetchone()[0]

print(f"✅ Setup tamamlandı! XP: 150, Frames: {frames}, Badges: {badges}")
conn.close()
