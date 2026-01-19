import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

print("Frames/Badges/Colors duplikatları temizleniyor...\n")

# Frames - her frame'in ilk kaydını tut
print("1. Frames tablosundan duplikatları temizle...")
c.execute("""
    DELETE FROM frames WHERE id NOT IN (
        SELECT MIN(id) FROM frames GROUP BY name
    )
""")
del_frames = c.rowcount
print(f"   {del_frames} duplicate frame silindi")

# Badges - her badge'in ilk kaydını tut
print("2. Badges tablosundan duplikatları temizle...")
c.execute("""
    DELETE FROM badges WHERE id NOT IN (
        SELECT MIN(id) FROM badges GROUP BY name
    )
""")
del_badges = c.rowcount
print(f"   {del_badges} duplicate badge silindi")

# Background colors - her color'ın ilk kaydını tut
print("3. Background_colors tablosundan duplikatları temizle...")
c.execute("""
    DELETE FROM background_colors WHERE id NOT IN (
        SELECT MIN(id) FROM background_colors GROUP BY name
    )
""")
del_colors = c.rowcount
print(f"   {del_colors} duplicate color silindi")

conn.commit()

# Kontrol
c.execute("SELECT COUNT(*) FROM frames")
frames = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM badges")
badges = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM background_colors")
colors = c.fetchone()[0]

print(f"\n✅ Temizlik tamamlandı!")
print(f"   Frames: {frames}")
print(f"   Badges: {badges}")
print(f"   Colors: {colors}")

conn.close()
