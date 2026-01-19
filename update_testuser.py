import sqlite3

DB_NAME = 'forum.db'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Test user'ı güncelleştirelim - eğer hash'lenmiyorsa düz password olarak tutalım
c.execute("""
    UPDATE users 
    SET email='testuser123@example.com', password='123456'
    WHERE name='testuser'
""")
conn.commit()

# Kontrol
c.execute("SELECT id, name, email, password FROM users WHERE name='testuser'")
user = c.fetchone()
if user:
    print(f"✅ Test user güncelleştirildi:")
    print(f"   ID: {user[0]}")
    print(f"   Name: {user[1]}")
    print(f"   Email: {user[2]}")
    print(f"   Password: {user[3]}")
else:
    print("❌ User bulunamadı")

conn.close()
