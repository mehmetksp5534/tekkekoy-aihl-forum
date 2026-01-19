"""
Profil Özelleştirme Sistemi - Veritabanı Migration Script
Bu script mevcut users tablosuna yeni sütunlar ekler ve
rozet, çerçeve, arka plan tabloları oluşturur.
"""

import sqlite3

DB_NAME = "forum.db"

def create_profile_customization_schema():
    """Profil özelleştirme tabloları oluşturur"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # 1. Users tablosuna yeni sütunlar ekle
        print("Users tablosuna sütunlar ekleniyor...")
        
        # XP sistemi
        try:
            c.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
            print("  ✓ xp sütunu eklendi")
        except:
            print("  ! xp sütunu zaten var")
        
        # Seçili çerçeve (frame_id)
        try:
            c.execute("ALTER TABLE users ADD COLUMN selected_frame_id INTEGER DEFAULT NULL")
            print("  ✓ selected_frame_id sütunu eklendi")
        except:
            print("  ! selected_frame_id sütunu zaten var")
        
        # Seçili arka plan rengi
        try:
            c.execute("ALTER TABLE users ADD COLUMN selected_bg_color_id INTEGER DEFAULT NULL")
            print("  ✓ selected_bg_color_id sütunu eklendi")
        except:
            print("  ! selected_bg_color_id sütunu zaten var")
        
        # Profil kartında gösterilecek rozet (badge_id)
        try:
            c.execute("ALTER TABLE users ADD COLUMN selected_badge_id INTEGER DEFAULT NULL")
            print("  ✓ selected_badge_id sütunu eklendi")
        except:
            print("  ! selected_badge_id sütunu zaten var")
        
        # 2. Frames (Çerçeveler) Tablosu
        print("\nFrames tablosu oluşturuluyor...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                image_path TEXT NOT NULL,
                required_xp INTEGER DEFAULT 0,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("  ✓ Frames tablosu hazır")
        
        # 3. Badges (Rozetler) Tablosu
        print("\nBadges tablosu oluşturuluyor...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon_path TEXT NOT NULL,
                required_xp INTEGER DEFAULT 0,
                badge_type TEXT DEFAULT 'activity',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("  ✓ Badges tablosu hazır")
        
        # 4. User Badges (Kullanıcı-Rozet İlişkisi)
        print("\nUser_badges tablosu oluşturuluyor...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id INTEGER NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (badge_id) REFERENCES badges(id),
                UNIQUE(user_id, badge_id)
            )
        ''')
        print("  ✓ User_badges tablosu hazır")
        
        # 5. Background Colors (Arka Plan Renkleri)
        print("\nBackground_colors tablosu oluşturuluyor...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS background_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color_code TEXT NOT NULL,
                gradient_code TEXT,
                required_xp INTEGER DEFAULT 0,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("  ✓ Background_colors tablosu hazır")
        
        # 6. User Frames (Kullanıcı-Çerçeve İlişkisi)
        print("\nUser_frames tablosu oluşturuluyor...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                frame_id INTEGER NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (frame_id) REFERENCES frames(id),
                UNIQUE(user_id, frame_id)
            )
        ''')
        print("  ✓ User_frames tablosu hazır")
        
        # 7. Varsayılan Çerçeveler (Default Frames)
        print("\nVarsayılan çerçeveler ekleniyor...")
        frames = [
            ("Klasik", "Düz siyah çerçeve", "/static/frames/classic.png", 0, 1),
            ("Altın", "Altın renkli görkemli çerçeve", "/static/frames/gold.png", 100, 0),
            ("Elmas", "Elmas taşlı lüks çerçeve", "/static/frames/diamond.png", 500, 0),
            ("Neon", "Neon ışık efektli modern çerçeve", "/static/frames/neon.png", 250, 0),
            ("Başarı", "Tamamlama sembolü çerçevesi", "/static/frames/achievement.png", 1000, 0),
        ]
        
        for name, desc, img_path, req_xp, is_default in frames:
            try:
                c.execute(
                    "INSERT INTO frames (name, description, image_path, required_xp, is_default) VALUES (?, ?, ?, ?, ?)",
                    (name, desc, img_path, req_xp, is_default)
                )
            except sqlite3.IntegrityError:
                pass
        
        # 8. Varsayılan Rozetler (Default Badges)
        print("Varsayılan rozetler ekleniyor...")
        badges = [
            ("Yeni Üye", "Forum'a yeni katıldı", "/static/badges/newbie.png", 0, "activity"),
            ("Etkin Katılımcı", "20 gönderi paylaştı", "/static/badges/active.png", 50, "activity"),
            ("Bilgi Ustası", "100 gönderi paylaştı", "/static/badges/expert.png", 200, "activity"),
            ("Hocaların Favorisi", "Öğretmenler tarafından beğenildi", "/static/badges/teacher_favorite.png", 300, "special"),
            ("Yardım Eli", "10 cevap verdi", "/static/badges/helper.png", 75, "activity"),
            ("Cevap Vermeci", "50 cevap verdi", "/static/badges/answerer.png", 300, "activity"),
            ("Forum Şampiyonu", "Ay'ın en aktif kullanıcısı", "/static/badges/champion.png", 500, "special"),
            ("Moderatör", "Forum moderatörü", "/static/badges/moderator.png", 1000, "special"),
        ]
        
        for name, desc, icon_path, req_xp, badge_type in badges:
            try:
                c.execute(
                    "INSERT INTO badges (name, description, icon_path, required_xp, badge_type) VALUES (?, ?, ?, ?, ?)",
                    (name, desc, icon_path, req_xp, badge_type)
                )
            except sqlite3.IntegrityError:
                pass
        
        # 9. Varsayılan Arka Plan Renkleri
        print("Varsayılan arka plan renkleri ekleniyor...")
        bg_colors = [
            ("Beyaz", "#FFFFFF", None, 0, 1),
            ("Açık Mavi", "#E8F4F8", None, 20, 0),
            ("Yumuşak Pembe", "#FFE8F0", None, 20, 0),
            ("Deniz Yeşili", "#E8F8F0", None, 20, 0),
            ("Altın", "#FFF8E8", None, 50, 0),
            ("Gece Modu Koyu", "#1A1A1A", None, 100, 0),
            ("Gradyan Mavi", "#E0F7FF", "linear-gradient(135deg, #E0F7FF, #B3E5FC)", 150, 0),
            ("Gradyan Mor", "#F3E5FF", "linear-gradient(135deg, #F3E5FF, #E1BEE7)", 200, 0),
        ]
        
        for name, color, gradient, req_xp, is_default in bg_colors:
            try:
                c.execute(
                    "INSERT INTO background_colors (name, color_code, gradient_code, required_xp, is_default) VALUES (?, ?, ?, ?, ?)",
                    (name, color, gradient, req_xp, is_default)
                )
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        print("\n✅ Veritabanı başarıyla güncellendi!")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_schema():
    """Mevcut şemayı gösterir"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 VERITABANI ŞEMASI")
    print("="*60)
    
    # Users tablosu
    print("\n1️⃣  USERS Tablosu:")
    c.execute("PRAGMA table_info(users)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    # Frames tablosu
    print("\n2️⃣  FRAMES Tablosu (Çerçeveler):")
    c.execute("PRAGMA table_info(frames)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    # Badges tablosu
    print("\n3️⃣  BADGES Tablosu (Rozetler):")
    c.execute("PRAGMA table_info(badges)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    # User_badges tablosu
    print("\n4️⃣  USER_BADGES Tablosu:")
    c.execute("PRAGMA table_info(user_badges)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    # Background_colors tablosu
    print("\n5️⃣  BACKGROUND_COLORS Tablosu:")
    c.execute("PRAGMA table_info(background_colors)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    # User_frames tablosu
    print("\n6️⃣  USER_FRAMES Tablosu:")
    c.execute("PRAGMA table_info(user_frames)")
    for row in c.fetchall():
        print(f"   {row[1]:25} | {row[2]}")
    
    print("\n" + "="*60)
    
    conn.close()

if __name__ == "__main__":
    create_profile_customization_schema()
    show_schema()
