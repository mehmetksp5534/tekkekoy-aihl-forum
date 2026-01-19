"""
XP artışını test et - yeni topic oluştur ve XP kontrol et
"""
import requests
import sqlite3

API_BASE = 'http://localhost:5000'
DB_NAME = 'forum.db'

# Session ile login yap
session = requests.Session()

login_data = {
    'email': 'testuser123@example.com',
    'password': '123456'
}

print("=" * 60)
print("XP ARTIS TEST")
print("=" * 60)

print("\n1. Önce veritabanında ilk XP'yi kontrol et...")
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("SELECT xp FROM users WHERE id=4")
initial_xp = c.fetchone()[0]
print(f"   Baslangic XP: {initial_xp}")
conn.close()

print("\n2. Login yapiliyor...")
response = session.post(f'{API_BASE}/login', data=login_data, allow_redirects=True)
print(f"   Status: {response.status_code}")

print("\n3. Home sayfasina erisiyor (topik olusturma formu icin)...")
home = session.get(f'{API_BASE}/')
print(f"   Status: {home.status_code}")

print("\n4. Yeni topic olusturuluyor...")
topic_data = {
    'title': 'Test Topic XP Increment',
    'category': 'genel',
    'content': 'This is a test topic to check XP increment system',
    'is_anonymous': 'off',
    'is_approved': 'on',
    'ask_teachers': 'off'
}

response = session.post(f'{API_BASE}/', data=topic_data, allow_redirects=True)
print(f"   Status: {response.status_code}")
print(f"   Final URL: {response.url}")

print("\n5. Veritabaninda XP artisini kontrol et...")
import time
time.sleep(1)  # Veritabanina yazilmasi icin bekle

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("SELECT xp FROM users WHERE id=4")
final_xp = c.fetchone()[0]
conn.close()

print(f"   Son XP: {final_xp}")
print(f"   Artis: {final_xp - initial_xp} XP")

if final_xp > initial_xp:
    print(f"\n   [OK] XP artis calisiyor! ({initial_xp} -> {final_xp})")
else:
    print(f"\n   [ERROR] XP artis olmadi!")

print("\n" + "=" * 60)
print("Test Tamamlandi!")
print("=" * 60)
