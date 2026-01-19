"""
Placeholder görseller oluşturma script'i
Profil çerçeveleri ve rozetleri için basit PNG görseller üretir.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Klasörleri tanımla
FRAMES_DIR = "static/frames"
BADGES_DIR = "static/badges"

def create_placeholder_image(filename, text, bg_color):
    """Placeholder PNG görsel oluştur"""
    # 64x64 görsel oluştur
    img = Image.new('RGB', (64, 64), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Metin ekle (basit şekil kullan)
    draw.rectangle([0, 0, 64, 64], outline='black', width=2)
    draw.text((32, 32), text, fill='white', anchor='mm')
    
    return img

def create_frames():
    """Çerçeve görselleri oluştur"""
    frames = [
        ('classic.png', '□', (33, 33, 33)),           # Siyah
        ('gold.png', '◆', (255, 215, 0)),              # Altın
        ('diamond.png', '◇', (230, 230, 250)),         # Elmas
        ('neon.png', '★', (0, 255, 255)),              # Neon
        ('achievement.png', '✓', (34, 139, 34)),       # Yeşil
    ]
    
    print("🖼️  Çerçeve görselleri oluşturuluyor...")
    for filename, text, color in frames:
        try:
            img = create_placeholder_image(filename, text, color)
            img.save(os.path.join(FRAMES_DIR, filename))
            print(f"   ✅ {filename}")
        except Exception as e:
            print(f"   ❌ {filename}: {e}")

def create_badges():
    """Rozet görselleri oluştur"""
    badges = [
        ('newbie.png', '🆕', (135, 206, 235)),        # Açık mavi
        ('active.png', '⚡', (255, 165, 0)),           # Turuncu
        ('expert.png', '★', (255, 215, 0)),            # Altın
        ('teacher_favorite.png', '❤', (220, 20, 60)), # Kırmızı
        ('helper.png', '👍', (50, 205, 50)),           # Yeşil
        ('answerer.png', '💬', (65, 105, 225)),        # Mavi
        ('champion.png', '👑', (218, 165, 32)),        # Koyu altın
        ('moderator.png', '🔑', (128, 0, 128)),        # Mor
    ]
    
    print("\n🏆 Rozet görselleri oluşturuluyor...")
    for filename, text, color in badges:
        try:
            img = create_placeholder_image(filename, text, color)
            img.save(os.path.join(BADGES_DIR, filename))
            print(f"   ✅ {filename}")
        except Exception as e:
            print(f"   ❌ {filename}: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("📸 PLACEHOLDER GÖRSELLERİ OLUŞTURULUYOR")
    print("="*50 + "\n")
    
    # PIL kurulu mu kontrol et
    try:
        from PIL import Image, ImageDraw
        create_frames()
        create_badges()
        print("\n✅ Tüm görseller başarıyla oluşturuldu!")
    except ImportError:
        print("⚠️  PIL (Pillow) kurulu değil!")
        print("Kurulum: pip install Pillow")
        print("\nAlternatif olarak, görselleri elle ekleyebilirsiniz:")
        print(f"  • {FRAMES_DIR}/ klasörüne çerçeve görselleri ekleyin")
        print(f"  • {BADGES_DIR}/ klasörüne rozet görselleri ekleyin")
        print("\n64x64 PNG görselleri kullanmanız önerilir.")
