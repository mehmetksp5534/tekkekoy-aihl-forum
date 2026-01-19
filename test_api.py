"""
Dashboard ve API test script'i - XP sistemi ve profil özelleştirmesini kontrol et
"""
import sqlite3
import requests
import json

DB_NAME = 'forum.db'
API_BASE = 'http://localhost:5000'

# Test user ID
USER_ID = 4

# Veritabanından doğrula
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

print("="*60)
print("📊 VERİTABANI KONTROL")
print("="*60)

# User bilgileri
c.execute("SELECT id, name, xp FROM users WHERE id=?", (USER_ID,))
user = c.fetchone()
if user:
    print(f"✅ User bulundu: ID={user[0]}, Name={user[1]}, XP={user[2]}")
else:
    print(f"❌ User bulunamadı: ID={USER_ID}")
    exit(1)

# Frames kontrol
c.execute("SELECT COUNT(*) FROM frames")
frames_count = c.fetchone()[0]
print(f"✅ Toplam Frames: {frames_count}")

c.execute("SELECT COUNT(*) FROM user_frames WHERE user_id=?", (USER_ID,))
user_frames_count = c.fetchone()[0]
print(f"✅ User {USER_ID} açılmış Frames: {user_frames_count}")

# Badges kontrol
c.execute("SELECT COUNT(*) FROM badges")
badges_count = c.fetchone()[0]
print(f"✅ Toplam Badges: {badges_count}")

c.execute("SELECT COUNT(*) FROM user_badges WHERE user_id=?", (USER_ID,))
user_badges_count = c.fetchone()[0]
print(f"✅ User {USER_ID} açılmış Badges: {user_badges_count}")

# Background colors kontrol
c.execute("SELECT COUNT(*) FROM background_colors")
colors_count = c.fetchone()[0]
print(f"✅ Toplam Background Colors: {colors_count}")

conn.close()

print("\n" + "="*60)
print("🔌 API ENDPOINT TEST")
print("="*60)

# Session setup - Flask'a session cookie'si olmazsa çalışmaz
# Bunun yerine ilk login yapacak şekilde test et ya da
# API endpoint'lerine doğrudan başını kontrol et

# 1. Test: /api/profile/frames endpoint'i var mı?
try:
    response = requests.get(f'{API_BASE}/api/profile/frames')
    print(f"\n1️⃣  GET /api/profile/frames")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ℹ️  Unauthorized (session gerekli)")
    elif response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response: {len(data)} frames")
        if data:
            print(f"   Sample: {json.dumps(data[0], indent=4, ensure_ascii=False)}")
    else:
        print(f"   ❌ Hata: {response.text}")
except Exception as e:
    print(f"   ❌ Bağlantı hatası: {e}")

# 2. Test: /api/profile/badges
try:
    response = requests.get(f'{API_BASE}/api/profile/badges')
    print(f"\n2️⃣  GET /api/profile/badges")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ℹ️  Unauthorized (session gerekli)")
    elif response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response: {len(data)} badges")
        if data:
            print(f"   Sample: {json.dumps(data[0], indent=4, ensure_ascii=False)}")
    else:
        print(f"   ❌ Hata: {response.text}")
except Exception as e:
    print(f"   ❌ Bağlantı hatası: {e}")

# 3. Test: /api/profile/bg-colors
try:
    response = requests.get(f'{API_BASE}/api/profile/bg-colors')
    print(f"\n3️⃣  GET /api/profile/bg-colors")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ℹ️  Unauthorized (session gerekli)")
    elif response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response: {len(data)} colors")
        if data:
            print(f"   Sample: {json.dumps(data[0], indent=4, ensure_ascii=False)}")
    else:
        print(f"   ❌ Hata: {response.text}")
except Exception as e:
    print(f"   ❌ Bağlantı hatası: {e}")

print("\n" + "="*60)
print("🔐 Session ile TEST (login gerekli)")
print("="*60)

# Session ile test - önce login yap
session = requests.Session()

# Login endpoint test
login_data = {
    'username': 'testuser',
    'password': '123456'
}

try:
    # İlk login'in yanında CSRF token alıp işle
    login_page = session.get(f'{API_BASE}/login')
    print(f"✅ Login sayfasına erişildi")
    
    # Form'u submit et
    response = session.post(f'{API_BASE}/login', data=login_data, allow_redirects=True)
    print(f"✅ Login request gönderildi: Status {response.status_code}")
    
    # Şimdi API'yi session ile kal
    frames_response = session.get(f'{API_BASE}/api/profile/frames')
    print(f"\n✅ Session ile /api/profile/frames çağrıldı: Status {frames_response.status_code}")
    
    if frames_response.status_code == 200:
        frames = frames_response.json()
        print(f"   Frames alındı: {len(frames)} adet")
        for i, frame in enumerate(frames[:3]):
            print(f"   {i+1}. {frame.get('name')} - Image: {frame.get('image')}")
    
    # Badges
    badges_response = session.get(f'{API_BASE}/api/profile/badges')
    print(f"\n✅ Session ile /api/profile/badges çağrıldı: Status {badges_response.status_code}")
    
    if badges_response.status_code == 200:
        badges = badges_response.json()
        print(f"   Badges alındı: {len(badges)} adet")
        for i, badge in enumerate(badges[:3]):
            print(f"   {i+1}. {badge.get('name')} - Icon: {badge.get('icon')}")
    
    # XP
    xp_response = session.get(f'{API_BASE}/api/profile/{USER_ID}')
    print(f"\n✅ Session ile /api/profile/{USER_ID} çağrıldı: Status {xp_response.status_code}")
    
    if xp_response.status_code == 200:
        user_data = xp_response.json()
        print(f"   User XP: {user_data.get('xp')}")
        print(f"   User Name: {user_data.get('name')}")
    
except Exception as e:
    print(f"❌ Hata: {e}")

print("\n" + "="*60)
print("✨ Test Tamamlandı!")
print("="*60)
