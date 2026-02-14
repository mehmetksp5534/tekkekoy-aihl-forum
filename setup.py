#!/usr/bin/env python3
"""
Tek komutla tüm kurulum yapan script
Kullanım: python3 setup.py
"""

import sqlite3
import os
import hashlib

DB_NAME = 'forum.db'

def setup_database():
    """Database ve tüm tabloları oluştur, admin hesabını ekle"""
    
    # Eski database'i sil
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"✅ Eski {DB_NAME} silindi")
    
    # Yeni database oluştur
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("📦 Tablolar oluşturuluyor...")
    
    # users tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
            bio TEXT,
            profile_photo TEXT,
            selected_frame_id INTEGER,
            selected_badge_id INTEGER,
            selected_background_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            night_mode INTEGER DEFAULT 0
        )
    """)
    
    # topics tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            content TEXT,
            author TEXT,
            solved INTEGER DEFAULT 0,
            attachment TEXT,
            is_anonymous INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 1,
            ask_teachers INTEGER DEFAULT 0
        )
    """)
    
    # replies tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            content TEXT,
            author TEXT,
            attachment TEXT
        )
    """)
    
    # badges tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            icon_path TEXT,
            description TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    # frames tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            description TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    # background_colors tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS background_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            color_code TEXT,
            gradient_code TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    # user_badges tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id INTEGER,
            badge_id INTEGER,
            PRIMARY KEY (user_id, badge_id)
        )
    """)
    
    # user_frames tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_frames (
            user_id INTEGER,
            frame_id INTEGER,
            PRIMARY KEY (user_id, frame_id)
        )
    """)
    
    print("✅ Tablolar oluşturuldu")
    
    # Admin hesabını ekle
    print("👤 Admin hesabı oluşturuluyor...")
    
    admin_name = 'Mehmet Emin Kasap'
    admin_email = 'mekacreative55@gmail.com'
    admin_password = 'MeKaC55_'
    
    hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
    
    c.execute("""
        INSERT INTO users (name, email, password, role, xp, level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (admin_name, admin_email, hashed_password, 'admin', 1000, 10))
    
    # Örnek rozet, çerçeve ve arka plan ekle
    print("🎨 Örnek dekorasyonlar ekleniyor...")
    
    c.execute("""
        INSERT INTO badges (name, icon_path, description, requirement)
        VALUES 
        ('Yeni Başlayan', 'badges/newbie.png', 'İlk başlayan kullanıcı', 0),
        ('Cevap Verici', 'badges/answerer.png', '10 cevap veren', 50),
        ('Aktivist', 'badges/active.png', '20 konu + cevap', 100),
        ('Uzman', 'badges/expert.png', '50 XP kazanan', 200),
        ('Yardımcı', 'badges/helper.png', 'Çok cevap veren', 150),
        ('Şampiyon', 'badges/champion.png', 'En aktif kullanıcı', 300),
        ('Moderatör', 'badges/moderator.png', 'Yönetici rozeti', 500),
        ('Öğretmen Sevgili', 'badges/teacher_favorite.png', 'Öğretmen tarafından seçildi', 250)
    """)
    
    c.execute("""
        INSERT INTO frames (name, image_path, description, requirement)
        VALUES 
        ('Basit', 'static/frames/classic.png', 'Klasik çerçeve', 0),
        ('Altın', 'static/frames/gold.png', 'Altın çerçeve', 100),
        ('Elmas', 'static/frames/diamond.png', 'Elmas çerçeve', 200),
        ('Neon', 'static/frames/neon.png', 'Neon çerçeve', 150),
        ('Başarı', 'static/frames/achievement.png', 'Başarı çerçevesi', 250)
    """)
    
    c.execute("""
        INSERT INTO background_colors (name, color_code, gradient_code, requirement)
        VALUES 
        ('Beyaz', '#FFFFFF', NULL, 0),
        ('Açık Mavi', '#E3F2FD', NULL, 0),
        ('Açık Yeşil', '#E8F5E9', NULL, 50),
        ('Açık Sarı', '#FFFDE7', NULL, 50),
        ('Açık Kırmızı', '#FFEBEE', NULL, 100),
        ('Koyu Mavi', '#1A237E', NULL, 200),
        ('Neon Yeşil Gradient', NULL, 'linear-gradient(135deg, #39FF14, #00FF00)', 250)
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Dekorasyonlar eklendi")
    print("\n" + "="*50)
    print("🎉 KURULUM TAMAMLANDI!")
    print("="*50)
    print(f"\n📧 Admin Kullanıcı Adı: {admin_name}")
    print(f"🔐 Admin Şifre: {admin_password}")
    print(f"📝 Admin Email: {admin_email}")
    print(f"\n🌐 http://127.0.0.1:5000 adresine gidin ve login yapın!")
    print("\n💡 Sonraki adım: python3 app.py ile uygulamayı başlatın")

if __name__ == '__main__':
    try:
        setup_database()
    except Exception as e:
        print(f"❌ Hata: {e}")