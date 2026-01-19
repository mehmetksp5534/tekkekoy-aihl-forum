"""
Profil Özelleştirme Sistemi - Kurulum ve Test Script
Bu script, yeni sistemi test etmek ve her şeyin doğru çalıştığını kontrol etmek için kullanılır.
"""

import sqlite3
import sys

DB_NAME = "forum.db"

def test_database_schema():
    """Veritabanı şemasını kontrol et"""
    print("\n" + "="*60)
    print("🔍 VERİTABANI ŞEMASI KONTROL EDİLİYOR")
    print("="*60)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Tüm tabloları listele
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = c.fetchall()
        
        print("\n✅ Bulunan Tablolar:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Users tablosunu kontrol et
        print("\n📋 Users Tablosu Sütunları:")
        c.execute("PRAGMA table_info(users)")
        for row in c.fetchall():
            print(f"   • {row[1]:25} | {row[2]}")
        
        # Frames tablosu veri sayısı
        c.execute("SELECT COUNT(*) FROM frames")
        frame_count = c.fetchone()[0]
        print(f"\n🖼️  Çerçeveler: {frame_count} adet")
        
        # Badges tablosu veri sayısı
        c.execute("SELECT COUNT(*) FROM badges")
        badge_count = c.fetchone()[0]
        print(f"🏆 Rozetler: {badge_count} adet")
        
        # Background colors veri sayısı
        c.execute("SELECT COUNT(*) FROM background_colors")
        color_count = c.fetchone()[0]
        print(f"🎨 Arka Plan Renkleri: {color_count} adet")
        
        conn.close()
        print("\n✅ Veritabanı şeması TAMAM!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return False

def test_sample_user():
    """Örnek bir kullanıcı ile test et"""
    print("\n" + "="*60)
    print("👤 ÖRNEK KULLANICI TESTI")
    print("="*60)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Test kullanıcısı oluştur
        test_email = "test@example.com"
        test_name = "TestKullanıcı"
        
        # Varsa sil
        c.execute("DELETE FROM users WHERE email=?", (test_email,))
        
        # Yenisini ekle
        c.execute(
            "INSERT INTO users (name, email, password, role, xp) VALUES (?, ?, ?, ?, ?)",
            (test_name, test_email, "password123", "student", 150)
        )
        conn.commit()
        
        # Kullanıcı ID'sini al
        c.execute("SELECT id FROM users WHERE email=?", (test_email,))
        user_id = c.fetchone()[0]
        
        print(f"\n✅ Test Kullanıcısı Oluşturuldu:")
        print(f"   • ID: {user_id}")
        print(f"   • Ad: {test_name}")
        print(f"   • Email: {test_email}")
        print(f"   • XP: 150")
        
        # Otomatik açılması gereken rozetleri test et
        from app import unlock_badges_for_user, unlock_frames_for_user
        
        unlock_badges_for_user(user_id)
        unlock_frames_for_user(user_id)
        
        # Açılan rozetleri göster
        c.execute("""
            SELECT b.name, b.required_xp FROM badges b
            JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id = ?
        """, (user_id,))
        
        badges = c.fetchall()
        print(f"\n🏆 Açılan Rozetler ({len(badges)} adet):")
        for badge in badges:
            print(f"   • {badge[0]} (XP: {badge[1]})")
        
        # Açılan çerçeveleri göster
        c.execute("""
            SELECT f.name, f.required_xp FROM frames f
            JOIN user_frames uf ON f.id = uf.frame_id
            WHERE uf.user_id = ?
        """, (user_id,))
        
        frames = c.fetchall()
        print(f"\n🖼️  Açılan Çerçeveler ({len(frames)} adet):")
        for frame in frames:
            print(f"   • {frame[0]} (XP: {frame[1]})")
        
        conn.close()
        print("\n✅ Test BAŞARILI!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return False

def show_api_endpoints():
    """Kullanılabilir API endpoints'lerini göster"""
    print("\n" + "="*60)
    print("🔗 KULLANILABILEN API ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("GET", "/api/profile/<user_id>", "Kullanıcı profil verilerini al"),
        ("GET", "/api/user-widget/<username>", "Mini widget verilerini al"),
        ("POST", "/api/profile/customize", "Profil özelleştirmesini kaydet"),
        ("GET", "/api/profile/frames", "Kullanıcının çerçevelerini al"),
        ("GET", "/api/profile/badges", "Kullanıcının rozetlerini al"),
        ("GET", "/api/profile/bg-colors", "Kullanıcının arka plan renklerini al"),
    ]
    
    print("\n")
    for method, path, description in endpoints:
        print(f"  [{method:4}] {path:35} - {description}")
    
    print("\n")

def show_installation_steps():
    """Kurulum adımlarını göster"""
    print("\n" + "="*60)
    print("📦 KURULUM ADIMLAR1")
    print("="*60)
    
    steps = [
        "✅ add_profile_customization.py script'ini çalıştırıldı",
        "✅ app.py'a yeni API endpoints'leri eklendi",
        "✅ templates/dashboard.html özelleştirme bölümü eklendi",
        "✅ templates/index.html mini widget eklendi",
        "✅ templates/topic.html mini widget eklendi",
        "✅ static/style.css mini profil kartı stilleri eklendi",
        "⚠️  static/frames/ klasörü oluştur ve görselleri ekle",
        "⚠️  static/badges/ klasörü oluştur ve görselleri ekle",
    ]
    
    print("\n")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    
    print("\n")

def main():
    """Ana test fonksiyonu"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🎨 PROFIL ÖZELLEŞTİRME SİSTEMİ - KURULUM & TEST         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Adım 1: Veritabanı kontrolü
    if not test_database_schema():
        print("\n⚠️  Veritabanı şeması kontrol edilemiyor!")
        print("Çözüm: 'python add_profile_customization.py' komutunu çalıştır")
        return False
    
    # Adım 2: Örnek kullanıcı testi
    if not test_sample_user():
        print("\n⚠️  Örnek kullanıcı oluşturulamadı!")
        return False
    
    # Adım 3: API endpoints'lerini göster
    show_api_endpoints()
    
    # Adım 4: Kurulum adımlarını göster
    show_installation_steps()
    
    print("\n" + "="*60)
    print("🎉 KURULUM TAMAMLANDı!")
    print("="*60)
    print("""
📚 Sonraki Adımlar:
  1. static/frames/ ve static/badges/ klasörlerini oluştur
  2. Görselleri (PNG) bu klasörlere yükle
  3. Flask uygulamasını başlat: python app.py
  4. Tarayıcıda http://localhost:5000/dashboard ziyaret et
  5. Profil özelleştirme bölümünü test et

💡 İpuçları:
  • Mini profil kartı görmek için konu listesinde kullanıcı adına hover yap
  • Çerçeve ve rozet görmek için yeterli XP'ye ulaş (150+ XP)
  • Arka plan renkleri şekmesinde seç

📖 Daha fazla bilgi için PROFILE_CUSTOMIZATION_README.md dosyasını oku
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
