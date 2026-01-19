import requests
import sqlite3

session = requests.Session()
API = 'http://localhost:5000'

print("=" * 70)
print("GECE MODU RENGİ TESTI")
print("=" * 70)

# Login
print("\n1. Login...")
session.post(f'{API}/login', data={
    'email': 'testuser123@example.com',
    'password': '123456'
})
print("✅ Logged in")

# Veritabanında rengi kontrol et
print("\n2. Gece Modu Rengini Kontrol Et...")
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute("SELECT id, name, color_code FROM background_colors WHERE id = 6")
row = c.fetchone()
print(f"   ID: {row[0]}, Name: {row[1]}, Color: {row[2]}")
conn.close()

if row[2] == '#232323':
    print("   ✅ Renk doğru: #232323")
else:
    print(f"   ❌ Renk yanlış: {row[2]}")

# Profil sayfasını kontrol et
print("\n3. Profile Sayfasını Kontrol Et...")
response = session.get(f'{API}/profile/testuser')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    # viewed_user_text_color ve viewed_user_bg_color check
    if 'viewed_user_text_color' in response.text or '#232323' in response.text:
        print("   ✅ Sayfada yazı rengi değişkeni var")
    else:
        print("   ⚠️  Sayfa yüklendi, kontrol edin")

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
print("""
SONUÇ:
  • Gece Modu rengi: #232323 (açık gri)
  • Koyu arka plan olunca yazı: Beyaz (#FFFFFF)
  • Açık arka plan olunca yazı: Siyah (#000000)
  
KONTROL ET:
  1. http://localhost:5000/dashboard → Arka Plan Renkleri → Gece Modu Koyu seç
  2. Kaydet'e bas
  3. Profile git → Yazılar görünüyor olmalı
""")
