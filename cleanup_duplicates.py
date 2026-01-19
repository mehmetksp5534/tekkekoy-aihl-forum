"""
user_frames ve user_badges tablosundan duplikatları temizle
"""
import sqlite3

DB_NAME = 'forum.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

print("Temizlik başlıyor...")

# user_frames'ten duplikatları sil, sadece ilk kaydı tut
print("\n1. user_frames duplikatları temizleniyor...")
c.execute("""
    DELETE FROM user_frames WHERE id NOT IN (
        SELECT MIN(id) FROM user_frames GROUP BY user_id, frame_id
    )
""")
deleted_frames = c.rowcount
print(f"   {deleted_frames} duplicate frame kaydı silindi")

# user_badges'ten duplikatları sil
print("\n2. user_badges duplikatları temizleniyor...")
c.execute("""
    DELETE FROM user_badges WHERE id NOT IN (
        SELECT MIN(id) FROM user_badges GROUP BY user_id, badge_id
    )
""")
deleted_badges = c.rowcount
print(f"   {deleted_badges} duplicate badge kaydı silindi")

conn.commit()

# Kontrol
c.execute("SELECT COUNT(*) FROM user_frames WHERE user_id=4")
frame_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM user_badges WHERE user_id=4")
badge_count = c.fetchone()[0]

print(f"\n✅ User 4 Frames: {frame_count} (unique)")
print(f"✅ User 4 Badges: {badge_count} (unique)")

conn.close()
