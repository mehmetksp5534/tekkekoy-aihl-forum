import requests
import json

API_BASE = 'http://localhost:5000'

print("=" * 60)
print("LOGIN TEST")
print("=" * 60)

# Session açalım
session = requests.Session()

# 1. Login sayfasını aç (CSRF token almazsa bile deneyelim)
print("\n1. Login sayfasına erişiliyor...")
login_page = session.get(f'{API_BASE}/login')
print(f"   Status: {login_page.status_code}")

# 2. Login form'u submit et
login_data = {
    'email': 'testuser123@example.com',
    'password': '123456'
}

print("\n2. Login form'u gönderiliyor...")
response = session.post(f'{API_BASE}/login', data=login_data, allow_redirects=True)
print(f"   Status: {response.status_code}")
print(f"   Final URL: {response.url}")

if 'dashboard' in response.url or response.status_code == 200:
    print(f"   [OK] Login başarılı!")
else:
    print(f"   [WARNING] Redirects yanlış olabilir")
    print(f"   Response content: {response.text[:200]}")

# 3. Dashboard'a erişmeyi dene
print("\n3. Dashboard'a erişiliyor...")
dashboard = session.get(f'{API_BASE}/dashboard')
print(f"   Status: {dashboard.status_code}")

# 4. API endpoint'lerine session ile erişim
print("\n" + "=" * 60)
print("API ENDPOINT TEST (Session ile)")
print("=" * 60)

# Frames
print("\n1. /api/profile/frames")
frames_response = session.get(f'{API_BASE}/api/profile/frames')
print(f"   Status: {frames_response.status_code}")
if frames_response.status_code == 200:
    frames = frames_response.json()
    print(f"   [OK] {len(frames)} frame alındı")
    if frames:
        print(f"   Sample Frame:")
        frame = frames[0]
        for key, value in frame.items():
            print(f"      {key}: {value}")
else:
    print(f"   [ERROR] {frames_response.text[:200]}")

# Badges
print("\n2. /api/profile/badges")
badges_response = session.get(f'{API_BASE}/api/profile/badges')
print(f"   Status: {badges_response.status_code}")
if badges_response.status_code == 200:
    badges = badges_response.json()
    print(f"   [OK] {len(badges)} badge alındı")
    if badges:
        print(f"   Sample Badge:")
        badge = badges[0]
        for key, value in badge.items():
            print(f"      {key}: {value}")
else:
    print(f"   [ERROR] {badges_response.text[:200]}")

# Colors
print("\n3. /api/profile/bg-colors")
colors_response = session.get(f'{API_BASE}/api/profile/bg-colors')
print(f"   Status: {colors_response.status_code}")
if colors_response.status_code == 200:
    colors = colors_response.json()
    print(f"   [OK] {len(colors)} color alındı")
    if colors:
        print(f"   Sample Color:")
        color = colors[0]
        for key, value in color.items():
            print(f"      {key}: {value}")
else:
    print(f"   [ERROR] {colors_response.text[:200]}")

# User profile
print("\n4. /api/profile/4 (User XP)")
user_response = session.get(f'{API_BASE}/api/profile/4')
print(f"   Status: {user_response.status_code}")
if user_response.status_code == 200:
    user = user_response.json()
    print(f"   [OK] User bilgileri:")
    print(f"      Name: {user.get('name')}")
    print(f"      XP: {user.get('xp')}")
else:
    print(f"   [ERROR] {user_response.text[:200]}")

print("\n" + "=" * 60)
print("Test Tamamland!")
print("=" * 60)
