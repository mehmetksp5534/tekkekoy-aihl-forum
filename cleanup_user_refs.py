import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

print("user_frames ve user_badges'i yeni frame/badge ID'lerine göre güncelle...\n")

# Eski frame ID'leri temizle (1,6,11 gibi yanlış olanlar)
# Sadece ID 1-5 aralığında olanları tut
c.execute("DELETE FROM user_frames WHERE frame_id > 5")
print(f"user_frames: Invalid frame_id'ler silindi")

# Aynı badge'ler için (1-8)
c.execute("DELETE FROM user_badges WHERE badge_id > 8")
print(f"user_badges: Invalid badge_id'ler silindi")

conn.commit()

# Kontrol
c.execute("SELECT COUNT(DISTINCT frame_id) FROM user_frames")
frames = c.fetchone()[0]
c.execute("SELECT COUNT(DISTINCT badge_id) FROM user_badges")
badges = c.fetchone()[0]

print(f"\n✅ Güncelleme tamamlandı!")
print(f"   Unique frames: {frames}")
print(f"   Unique badges: {badges}")

conn.close()
