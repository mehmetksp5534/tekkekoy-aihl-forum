import sqlite3
import hashlib

DB_NAME = 'forum.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Test kullanıcı
username = 'testuser'
password = hashlib.sha256(b'123456').hexdigest()

# Kullanıcı var mı kontrol et
c.execute("SELECT id FROM users WHERE name=?", (username,))
user = c.fetchone()

if user:
    user_id = user[0]
    print(f"Test user zaten var (ID: {user_id})")
else:
    c.execute("INSERT INTO users (name, email, password, role, bio, xp) VALUES (?, ?, ?, 'user', 'Test User', 0)",
              (username, 'test@example.com', password))
    conn.commit()
    user_id = c.lastrowid
    print(f"Test user oluşturuldu (ID: {user_id})")

# XP güncelle
c.execute("UPDATE users SET xp=? WHERE id=?", (150, user_id))
conn.commit()

# user_frames ve user_badges'e ekle
c.execute("""
    SELECT f.id FROM frames f 
    WHERE NOT EXISTS (SELECT 1 FROM user_frames WHERE user_id=? AND frame_id=f.id)
""", (user_id,))
frames = c.fetchall()
for frame in frames:
    c.execute("INSERT OR IGNORE INTO user_frames (user_id, frame_id) VALUES (?, ?)", (user_id, frame[0]))

c.execute("""
    SELECT b.id FROM badges b 
    WHERE NOT EXISTS (SELECT 1 FROM user_badges WHERE user_id=? AND badge_id=b.id)
""", (user_id,))
badges = c.fetchall()
for badge in badges:
    c.execute("INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, badge[0]))

conn.commit()

# Kontrol et
c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
print(f"Test user XP: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM user_frames WHERE user_id=?", (user_id,))
print(f"Test user açılmış frames: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM user_badges WHERE user_id=?", (user_id,))
print(f"Test user açılmış badges: {c.fetchone()[0]}")

conn.close()
print("\n✅ Test setup tamamlandı!")
