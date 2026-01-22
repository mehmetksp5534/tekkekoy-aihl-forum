import sqlite3
import hashlib
import os

DB_NAME = 'forum.db'

def create_admin():
    """Admin hesabını oluştur"""
    
    # Database kontrol et
    if not os.path.exists(DB_NAME):
        print(f"❌ Hata: {DB_NAME} dosyası bulunamadı!")
        print("Lütfen önce app.py'yi çalıştırıp database'i oluşturun.")
        return False
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Admin bilgileri
        admin_name = 'Mehmet Emin Kasap'
        admin_email = 'mekacreative55@gmail.com'
        admin_password = 'MeKaC55_'
        
        # Şifreyi hash'le
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
        
        # Admin hesabını ekle
        c.execute("""
            INSERT INTO users (name, email, password, role, xp, level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (admin_name, admin_email, hashed_password, 'admin', 1000, 10))
        
        conn.commit()
        conn.close()
        
        print("✅ Admin hesabı başarıyla oluşturuldu!")
        print(f"📧 Kullanıcı Adı: {admin_name}")
        print(f"🔐 Şifre: {admin_password}")
        print(f"📝 Email: {admin_email}")
        print(f"⭐ XP: 1000")
        print(f"🎖️  Level: 10")
        print(f"\n🌐 http://127.0.0.1:5000 adresine gidip login yapabilirsiniz.")
        
        return True
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Hata: {admin_name} adında bir kullanıcı zaten var!")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False

if __name__ == '__main__':
    create_admin()