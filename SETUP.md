# 🚀 Profil Özelleştirme Sistemi - KURULUM KILAVUZU

## ⚡ Hızlı Başlangıç (5 Dakika)

### Adım 1: Migration Script'i Çalıştır
```bash
python add_profile_customization.py
```
**Ne yapıyor?**
- ✅ Users tablosuna 4 yeni sütun ekler
- ✅ 6 yeni tablo oluşturur (frames, badges, vb.)
- ✅ Varsayılan veri (5 çerçeve, 8 rozet, 8 renk) ekler

### Adım 2: Testet Et
```bash
python test_profile_customization.py
```
**Beklenen çıktı:**
```
✅ Bulunan Tablolar: 9 adet
✅ Veritabanı şeması TAMAM!
✅ Test Kullanıcısı Oluşturuldu
✅ Test BAŞARILI!
```

### Adım 3: Görselleri Oluştur
```bash
python create_placeholder_images.py
```

### Adım 4: Flask Uygulamasını Başlat
```bash
python app.py
```

### Adım 5: Tarayıcıda Test Et
```
http://localhost:5000/dashboard
```

---

## 📦 İçerilen Dosyalar

### Yeni Python Script'leri
| Dosya | Açıklama |
|-------|----------|
| `add_profile_customization.py` | Veritabanı migration |
| `test_profile_customization.py` | Sistem testi |
| `create_placeholder_images.py` | Placeholder görsel üretici |

### Güncellenmiş Dosyalar
| Dosya | Değişiklikler |
|-------|--------------|
| `app.py` | 7 yeni API endpoint |
| `templates/dashboard.html` | Profil özelleştirme UI |
| `templates/index.html` | Mini widget + JS |
| `templates/topic.html` | Mini widget + JS |
| `static/style.css` | 150+ satır CSS |

### Yeni Klasörler
```
static/frames/       → Çerçeve görselleri (5x PNG)
static/badges/       → Rozet görselleri (8x PNG)
```

---

## 🔧 Ayrıntılı Kurulum

### Gereksinimler
- Python 3.7+
- Flask
- SQLite3 (dahili)
- Pillow (isteğe bağlı, görseller için)

### Adım Adım Talimatlar

#### 1. Veritabanını Güncelle
```bash
$ python add_profile_customization.py
```

**Çıktı:**
```
Users tablosuna sütunlar ekleniyor...
  ✓ xp sütunu eklendi
  ✓ selected_frame_id sütunu eklendi
  ✓ selected_bg_color_id sütunu eklendi
  ✓ selected_badge_id sütunu eklendi

Frames tablosu oluşturuluyor...
  ✓ Frames tablosu hazır
  
[... daha fazla ...]

✅ Veritabanı başarıyla güncellendi!
```

#### 2. Klasörleri Oluştur
```bash
# Windows
mkdir static\frames
mkdir static\badges

# Linux/Mac
mkdir -p static/frames
mkdir -p static/badges
```

#### 3. Placeholder Görselleri Oluştur
```bash
$ python create_placeholder_images.py
```

**Pillow yüklü değilse:**
```bash
pip install Pillow
```

**Veya manuel görseller:**
- 64x64 PNG dosyalarını oluşturun
- `static/frames/` klasörüne koyun
- `static/badges/` klasörüne koyun

#### 4. Uygulamayı Başlat
```bash
$ python app.py
```

**Beklenen çıktı:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

#### 5. Tarayıcıda Test Et
Açık: `http://localhost:5000`

---

## 🎯 Özellik Testi

### Test 1: Profil Özelleştirme Sayfası
1. Giriş yap
2. `/dashboard` git
3. Aşağı kaydır → "Profil Özelleştirmesi" bölümünü gör
4. 3 sekmeyi test et:
   - 🖼️ Çerçeveler
   - 🏆 Rozetler
   - 🎨 Arka Plan Renkleri

### Test 2: Mini Profil Kartı
1. Ana sayfaya git (`/`)
2. Konu listesini gör
3. Konu açan kişinin adına hover yap
4. Mini profil kartı açılmalı

### Test 3: Cevaplarda Widget
1. Herhangi bir konuyu aç
2. Cevapları gör
3. Cevap veren kişinin adına hover yap
4. Mini profil kartı açılmalı

### Test 4: XP Sistemi
1. Konu aç → +10 XP
2. Cevap ver → +5 XP
3. Dashboard'a git
4. XP artışını gözlemle

### Test 5: Otomatik Rozet Açılması
1. 150+ XP'ye ulaş
2. Dashboard'a git
3. Rozetler sekmesinde 3 rozet görülmeli:
   - Yeni Üye (0 XP)
   - Etkin Katılımcı (50 XP)
   - Yardım Eli (75 XP)

---

## 📱 API Endpoints

### 1. Profil Verilerini Al
```
GET /api/profile/<user_id>

Yanıt:
{
    "id": 1,
    "name": "Ahmet",
    "xp": 150,
    "selected_frame": { "id": 2, "name": "Altın", "image": "..." },
    "selected_badge": { "id": 3, "name": "Bilgi Ustası", "icon": "..." },
    "all_badges": [...]
}
```

### 2. Mini Widget Verilerini Al
```
GET /api/user-widget/<username>

Yanıt:
{
    "id": 1,
    "name": "Ahmet",
    "profile_photo": "profile_1_123456.jpg",
    "role": "student",
    "xp": 150,
    "frame_image": "/static/frames/gold.png",
    "badge_icon": "/static/badges/expert.png"
}
```

### 3. Profili Özelleştir
```
POST /api/profile/customize
Content-Type: application/json

{
    "frame_id": 2,
    "badge_id": 3,
    "bg_color_id": 7
}
```

### 4. Açılan Çerçeveleri Al
```
GET /api/profile/frames

Yanıt:
[
    { "id": 1, "name": "Klasik", "image": "...", "xp_required": 0 },
    { "id": 2, "name": "Altın", "image": "...", "xp_required": 100 }
]
```

### 5. Açılan Rozetleri Al
```
GET /api/profile/badges

Yanıt:
[
    { "id": 1, "name": "Yeni Üye", "icon": "...", "xp_required": 0 },
    { "id": 3, "name": "Bilgi Ustası", "icon": "...", "xp_required": 200 }
]
```

### 6. Açılan Renkler Al
```
GET /api/profile/bg-colors

Yanıt:
[
    { "id": 1, "name": "Beyaz", "color": "#FFFFFF", "xp_required": 0 },
    { "id": 2, "name": "Açık Mavi", "color": "#E8F4F8", "xp_required": 20 }
]
```

---

## 🐛 Sorun Giderme

### Problem: "Mini profil kartı açılmıyor"
**Çözüm:**
1. Tarayıcı konsolunu aç (F12)
2. Hata mesajını kontrol et
3. `/api/user-widget/<username>` endpoint'ini test et:
   ```
   curl http://localhost:5000/api/user-widget/AhmetAdı
   ```

### Problem: "Rozetler açılmıyor"
**Çözüm:**
```python
# Python shell'de test et
from app import calculate_user_xp, unlock_badges_for_user
calculate_user_xp(1)  # user_id = 1
unlock_badges_for_user(1)
```

### Problem: "XP güncellenmiyor"
**Çözüm:**
```python
# app.py'da calculate_user_xp() çağrısını test et
from app import calculate_user_xp
calculate_user_xp(1)
```

### Problem: "Görseller yüklenmez"
**Çözüm:**
1. `static/frames/` klasörü var mı kontrol et
2. PNG dosyaları klasörde var mı kontrol et
3. Dosya yollarını kontrol et (app.py'da)

---

## 📊 Veritabanı Yapısı (Özet)

```sql
-- Users tablosuna eklenen sütunlar:
xp INTEGER DEFAULT 0
selected_frame_id INTEGER
selected_badge_id INTEGER
selected_bg_color_id INTEGER

-- Yeni Tablolar:
frames (id, name, image_path, required_xp, ...)
badges (id, name, icon_path, required_xp, ...)
background_colors (id, name, color_code, required_xp, ...)
user_badges (id, user_id, badge_id, unlocked_at)
user_frames (id, user_id, frame_id, unlocked_at)
```

---

## 🎨 Özelleştirme

### Yeni Çerçeve Ekle
```python
# app.py'da add_profile_customization.py açıp frames listesini güncelle
frames = [
    ("Klasik", "Düz siyah çerçeve", "/static/frames/classic.png", 0, 1),
    ("Yeni Çerçeve", "Açıklama", "/static/frames/new.png", 200, 0),  # YENİ
    ...
]
```

### Yeni Rozet Ekle
```python
badges = [
    ("Yeni Üye", "Forum'a yeni katıldı", "/static/badges/newbie.png", 0, "activity"),
    ("Yeni Rozet", "Açıklama", "/static/badges/new.png", 150, "activity"),  # YENİ
    ...
]
```

### Renk Şeması Değiştir
```python
# dashboard.html'de customization-section renklerini güncelle
background: linear-gradient(135deg, #YENI_RENK 0%, #YENİ_RENK 100%);
```

---

## 📚 Kaynaklar

- **Veritabanı Şeması**: [PROFILE_CUSTOMIZATION_README.md](PROFILE_CUSTOMIZATION_README.md)
- **Flask API**: https://flask.palletsprojects.com/
- **SQLite**: https://sqlite.org/docs.html
- **JavaScript Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

## ✅ Kontrol Listesi

- [ ] `add_profile_customization.py` çalıştırıldı
- [ ] `test_profile_customization.py` başarılı
- [ ] `static/frames/` klasörü oluşturuldu
- [ ] `static/badges/` klasörü oluşturuldu
- [ ] Görseller oluşturuldu veya manuel eklenildi
- [ ] Flask uygulaması başlatıldı
- [ ] `/dashboard` sayfası kontrol edildi
- [ ] Mini profil kartı test edildi
- [ ] XP sistemi test edildi
- [ ] Rozetler test edildi

---

## 🎉 Tebrikler!

Profil Özelleştirme Sistemi başarıyla kuruldu!

**İletişim & Destek:**
- Sorunlar için issue açın
- Önerileri paylaşın
- Dokümantasyonu güncelleyin

**Sürüm:** 1.0.0
**Son Güncelleme:** 2026-01-11
