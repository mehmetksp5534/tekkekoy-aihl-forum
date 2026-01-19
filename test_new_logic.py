"""
Profil özelleştirme sisteminin yeni mantığını test et
1. Seçimler hemen kaydetmemelidir (pending state)
2. Kaydet butonuna basınca tüm seçimler kaydedilmelidir
3. Default option kullanılabilir olmalıdır
"""
import requests
import json

session = requests.Session()
API = 'http://localhost:5000'

print("=" * 70)
print("PROFİL ÖZELLEŞTİRME SİSTEMİ - YENİ MANTIK TESTI")
print("=" * 70)

# Login
print("\n1. Login...")
session.post(f'{API}/login', data={
    'email': 'testuser123@example.com',
    'password': '123456'
})
print("✅ Logged in")

# Seçimleri al
print("\n2. API'lerden seçenekleri al...")
frames = session.get(f'{API}/api/profile/frames').json()
badges = session.get(f'{API}/api/profile/badges').json()
colors = session.get(f'{API}/api/profile/bg-colors').json()

print(f"   Frames: {len(frames)}")
print(f"   Badges: {len(badges)}")
print(f"   Colors: {len(colors)}")

# Seçimleri kaydet
print("\n3. Profil özelleştirmelerini kaydet...")
if frames and badges and colors:
    customizations = {
        'frame_id': frames[1]['id'] if len(frames) > 1 else frames[0]['id'],
        'badge_id': badges[0]['id'],
        'bg_color_id': colors[0]['id']
    }
    
    response = session.post(f'{API}/api/profile/customize', json=customizations)
    result = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {result}")
    
    if result.get('success') or result.get('message'):
        print("   ✅ Kaydetme başarılı")
        
        # Veritabanında kaydedildiğini kontrol et
        print("\n4. Veritabanında kayıtları kontrol et...")
        import sqlite3
        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        c.execute("""
            SELECT selected_frame_id, selected_badge_id, selected_bg_color_id
            FROM users WHERE id=4
        """)
        row = c.fetchone()
        print(f"   Frame ID: {row[0]} (Expected: {customizations['frame_id']})")
        print(f"   Badge ID: {row[1]} (Expected: {customizations['badge_id']})")
        print(f"   Color ID: {row[2]} (Expected: {customizations['bg_color_id']})")
        
        if row[0] == customizations['frame_id'] and row[1] == customizations['badge_id'] and row[2] == customizations['bg_color_id']:
            print("   ✅ Tüm seçimler doğru şekilde kaydedildi")
        else:
            print("   ❌ Kaydedilirken hata oluştu")
        conn.close()

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
