import sqlite3

conn = sqlite3.connect('forum.db')
c = conn.cursor()

# Frames kontrolü
c.execute("SELECT id, name FROM frames")
frames = c.fetchall()
print(f"Total Frames in DB: {len(frames)}")
for f in frames:
    print(f"  {f}")

# user_frames kontrolü
c.execute("SELECT user_id, frame_id FROM user_frames WHERE user_id=4")
uf = c.fetchall()
print(f"\nUser 4 in user_frames: {len(uf)} entries")
for u in uf:
    print(f"  user_id={u[0]}, frame_id={u[1]}")

conn.close()
