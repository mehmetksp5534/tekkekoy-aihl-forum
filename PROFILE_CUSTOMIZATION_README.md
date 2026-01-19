# 🎨 Profil Özelleştirme Sistemi - Kurulum & Kullanım Rehberi

## 📋 İçindekiler
1. [Sistem Özellikleri](#sistem-özellikleri)
2. [Veritabanı Şeması](#veritabanı-şeması)
3. [Kurulum Adımları](#kurulum-adımları)
4. [API Endpoints](#api-endpoints)
5. [Kullanıcı Arayüzü](#kullanıcı-arayüzü)
6. [Teknik Detaylar](#teknik-detaylar)

---

## 🌟 Sistem Özellikleri

### ✨ Ana Özellikler
- **Profil Fotoğrafı (PP)**: Kullanıcılar sadece PP yükleyebilir
- **Dinamik Çerçeveler**: 5 farklı çerçeve (Klasik, Altın, Elmas, Neon, Başarı)
- **Rozetler**: 8 farklı rozet (Aktivite, Başarı ve Özel görevler için)
- **Arka Plan Renkleri**: 8 renk ve gradyan seçeneği
- **Mini Profil Kartı**: Kullanıcı adına hover yapıldığında açılan popup
- **XP Sistemi**: 
  - Konu açma = 10 XP
  - Cevap verme = 5 XP
  - Otomatik çerçeve ve rozet açılması

### 🎯 Gösterim Yerleri
1. **Konu Listesinde** (index.html): Konu açan kişinin adının yanında
2. **Konu Detayında** (topic.html): Cevap veren kişilerin adlarının yanında
3. **Mini Profil Kartında**: Hover yapıldığında açılan detaylı profil bilgisi

---

## 🗄️ Veritabanı Şeması

### 1. **users** Tablosu (Mevcut + Yeni Sütunlar)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    bio TEXT,
    profile_photo TEXT,
    xp INTEGER DEFAULT 0,                    -- ⭐ YENI
    selected_frame_id INTEGER DEFAULT NULL,  -- ⭐ YENI
    selected_badge_id INTEGER DEFAULT NULL,  -- ⭐ YENI
    selected_bg_color_id INTEGER DEFAULT NULL -- ⭐ YENI
)
```

### 2. **frames** Tablosu (YENİ)
```sql
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                      -- "Altın", "Elmas" vb.
    description TEXT,                        -- Açıklama
    image_path TEXT NOT NULL,                -- /static/frames/gold.png
    required_xp INTEGER DEFAULT 0,           -- Açılması için gerekli XP
    is_default BOOLEAN DEFAULT 0,            -- Varsayılan çerçeve
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Varsayılan Çerçeveler:**
| id | name | required_xp |
|----|------|------------|
| 1 | Klasik | 0 |
| 2 | Altın | 100 |
| 3 | Elmas | 500 |
| 4 | Neon | 250 |
| 5 | Başarı | 1000 |

### 3. **badges** Tablosu (YENİ)
```sql
CREATE TABLE badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                      -- "Yeni Üye", "Bilgi Ustası" vb.
    description TEXT,                        -- Rozet açıklaması
    icon_path TEXT NOT NULL,                 -- /static/badges/expert.png
    required_xp INTEGER DEFAULT 0,           -- Açılması için gerekli XP
    badge_type TEXT DEFAULT 'activity',      -- 'activity', 'special'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Varsayılan Rozetler:**
| id | name | required_xp | badge_type |
|----|------|------------|-----------|
| 1 | Yeni Üye | 0 | activity |
| 2 | Etkin Katılımcı | 50 | activity |
| 3 | Bilgi Ustası | 200 | activity |
| 4 | Hocaların Favorisi | 300 | special |
| 5 | Yardım Eli | 75 | activity |
| 6 | Cevap Vermeci | 300 | activity |
| 7 | Forum Şampiyonu | 500 | special |
| 8 | Moderatör | 1000 | special |

### 4. **user_badges** Tablosu (YENİ)
```sql
CREATE TABLE user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id),
    UNIQUE(user_id, badge_id)               -- Aynı rozet bir kullanıcıya sadece bir kez
)
```

### 5. **background_colors** Tablosu (YENİ)
```sql
CREATE TABLE background_colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                      -- "Beyaz", "Açık Mavi" vb.
    color_code TEXT NOT NULL,                -- "#FFFFFF"
    gradient_code TEXT,                      -- İsteğe bağlı gradyan
    required_xp INTEGER DEFAULT 0,           -- Açılması için gerekli XP
    is_default BOOLEAN DEFAULT 0,            -- Varsayılan renk
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Varsayılan Renkler:**
| id | name | color_code | gradient_code | required_xp |
|----|------|-----------|--------------|------------|
| 1 | Beyaz | #FFFFFF | - | 0 |
| 2 | Açık Mavi | #E8F4F8 | - | 20 |
| 3 | Yumuşak Pembe | #FFE8F0 | - | 20 |
| 4 | Deniz Yeşili | #E8F8F0 | - | 20 |
| 5 | Altın | #FFF8E8 | - | 50 |
| 6 | Gece Modu Koyu | #1A1A1A | - | 100 |
| 7 | Gradyan Mavi | #E0F7FF | linear-gradient(...) | 150 |
| 8 | Gradyan Mor | #F3E5FF | linear-gradient(...) | 200 |

### 6. **user_frames** Tablosu (YENİ)
```sql
CREATE TABLE user_frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (frame_id) REFERENCES frames(id),
    UNIQUE(user_id, frame_id)               -- Aynı çerçeve bir kullanıcıya sadece bir kez
)
```

---

## 🚀 Kurulum Adımları

### 1. Veritabanını Güncelle
Migration script'ini çalıştırın:

```bash
python add_profile_customization.py
```

Bu script otomatik olarak:
- ✅ Users tablosuna 4 yeni sütun ekler
- ✅ frames, badges, background_colors, user_badges, user_frames tablolarını oluşturur
- ✅ Varsayılan çerçeveler, rozetler ve renkleri ekler

### 2. Statik Dosyaları Oluştur
Profil görselleri için klasörler oluşturun:

```bash
mkdir -p static/frames
mkdir -p static/badges
```

**Placeholder görseller ekleyin** (16x16 PNG dosyaları):
- `static/frames/classic.png` - Klasik çerçeve
- `static/frames/gold.png` - Altın çerçeve
- `static/frames/diamond.png` - Elmas çerçeve
- `static/frames/neon.png` - Neon çerçeve
- `static/frames/achievement.png` - Başarı çerçevesi
- `static/badges/newbie.png` - Yeni üye rozeti
- `static/badges/active.png` - Etkin katılımcı rozeti
- vb. (8 tane rozet görseli)

### 3. Flask Uygulamasını Yeniden Başlat
```bash
python app.py
```

---

## 🔗 API Endpoints

### 1. Kullanıcı Profil Verilerini Al
```
GET /api/profile/<user_id>
```
**Yanıt:**
```json
{
    "id": 1,
    "name": "Ahmet",
    "bio": "Matematik öğrenci",
    "profile_photo": "profile_1_123456.jpg",
    "xp": 250,
    "role": "student",
    "selected_frame": {
        "id": 2,
        "name": "Altın",
        "image": "/static/frames/gold.png"
    },
    "selected_badge": {
        "id": 3,
        "name": "Bilgi Ustası",
        "icon": "/static/badges/expert.png"
    },
    "selected_bg_color": {
        "id": 7,
        "color": "#E0F7FF",
        "gradient": "linear-gradient(135deg, #E0F7FF, #B3E5FC)"
    },
    "all_badges": [
        {"id": 1, "name": "Yeni Üye", "icon": "/static/badges/newbie.png"},
        {"id": 3, "name": "Bilgi Ustası", "icon": "/static/badges/expert.png"}
    ]
}
```

### 2. Mini Widget Verilerini Al
```
GET /api/user-widget/<username>
```
**Yanıt:**
```json
{
    "id": 1,
    "name": "Ahmet",
    "profile_photo": "profile_1_123456.jpg",
    "role": "student",
    "xp": 250,
    "frame_image": "/static/frames/gold.png",
    "badge_icon": "/static/badges/expert.png"
}
```

### 3. Profili Özelleştir
```
POST /api/profile/customize
Content-Type: application/json

{
    "frame_id": 2,      // İsteğe bağlı
    "badge_id": 3,      // İsteğe bağlı
    "bg_color_id": 7    // İsteğe bağlı
}
```

### 4. Kullanıcının Çerçevelerini Al
```
GET /api/profile/frames
```

### 5. Kullanıcının Rozetlerini Al
```
GET /api/profile/badges
```

### 6. Kullanıcının Arka Plan Renklerini Al
```
GET /api/profile/bg-colors
```

---

## 🎨 Kullanıcı Arayüzü

### Dashboard (Profil Özelleştirme Sayfası)
**Konum:** `/dashboard`

#### Özellikler:
1. **XP Göstergesi**: Toplam XP'yi görüntüler
2. **3 Sekme**:
   - 🖼️ Çerçeveler
   - 🏆 Rozetler
   - 🎨 Arka Plan Renkleri

3. **Grid Görünümü**: Her öğe için
   - Görsel
   - Ad
   - Gerekli XP
   - Kilit/Seçili durumu

#### Etkileşim:
- Öğeyi tıkla → Seç
- Seçili öğeler mavi renkte vurgulanır
- Kilitli öğeler 🔒 işareti gösterir

### Index (Konu Listesi)
**Mini Widget Gösterimi:**
```
📝 Açan: [Avatar] Ahmet Öğrenci
         └─ Hover → Mini Profil Kartı Açılır
```

### Topic (Konu Detayı)
**Cevaplarda Mini Widget:**
```
[Avatar] Ayşe
└─ Hover → Mini Profil Kartı Açılır
```

### Mini Profil Kartı (Popup)
Hover yapıldığında açılan popup:
```
╔════════════════════╗
║   [Avatar]         │
║   Ahmet Yılmaz     │
║   👨‍🎓 Öğrenci       │
║   ⭐ 250 XP        │
╠════════════════════╣
║ 250 | 👨‍🎓         │
║ XP  | Rol         │
╠════════════════════╣
║   Rozetler:        │
║ [🏆] [🏅] [⭐]    │
╠════════════════════╣
║ Profili Görüntüle →│
╚════════════════════╝
```

---

## 🔧 Teknik Detaylar

### XP Hesaplaması
```python
# app.py içinde calculate_user_xp() fonksiyonu
topic_count = COUNT(*) FROM topics WHERE author = user_id
reply_count = COUNT(*) FROM replies WHERE author = user_id
total_xp = (topic_count * 10) + (reply_count * 5)
```

### Otomatik Rozet Açılması
```python
# unlock_badges_for_user() fonksiyonu
# XP >= required_xp olan tüm rozetler otomatik açılır
```

### Otomatik Çerçeve Açılması
```python
# unlock_frames_for_user() fonksiyonu
# XP >= required_xp olan tüm çerçeveler otomatik açılır
```

### Mini Profil Kartı JavaScript
```javascript
// loadMiniProfileCards() fonksiyonu
// Her .user-widget-container için:
// 1. /api/user-widget/<username> endpoint'ini çağır
// 2. Profil fotoğrafı, rozet, çerçeve verilerini al
// 3. Mini kartı DOM'a ekle
// 4. Hover event'ine bağla
```

### CSS Animasyonları
- **Slide Down**: Mini kartın açılması (0.2s)
- **Hover Transform**: Widget'lar yukarı kaymı (-2px)
- **Box Shadow**: Derinlik efekti

---

## 📝 Dosya Değişiklikleri Özeti

### Yeni Dosyalar
1. `add_profile_customization.py` - Migration script

### Güncellenmiş Dosyalar
1. `app.py` - 7 yeni API endpoint
2. `templates/dashboard.html` - Profil özelleştirme bölümü
3. `templates/index.html` - Mini widget + JavaScript
4. `templates/topic.html` - Mini widget + JavaScript
5. `static/style.css` - Mini profil kartı stilleri

### Yeni Klasörler
- `static/frames/` - Çerçeve görselleri
- `static/badges/` - Rozet görselleri

---

## 🐛 Sorun Giderme

### Mini Profil Kartı Açılmıyor
- Tarayıcı konsolunu kontrol et (F12)
- `/api/user-widget/<username>` endpoint'ini test et

### XP Güncellenmiyor
- `calculate_user_xp()` fonksiyonunu el ile çağır:
  ```python
  # dashboard.py
  from app import calculate_user_xp
  calculate_user_xp(user_id)
  ```

### Rozet/Çerçeve Açılmıyor
- Migration script'i yeniden çalıştır
- `unlock_badges_for_user()` ve `unlock_frames_for_user()` fonksiyonlarını test et

---

## 💡 İleri Özellikler (Opsiyonel)

### Yakın Zamanda Eklenebilecek
1. **Durum Mesajları**: Kullanıcı profil kartında "Çevrimiçi" durumu
2. **Başarı Sistemi**: Görevleri tamamlama (100 konu vb.)
3. **Aylık Rozeti**: "Ay'ın En Aktif Kullanıcısı" otomatik seçilmesi
4. **Özel Çerçeveler**: Admin tarafından belirli kullanıcılara verilen çerçeveler
5. **Profil Kartı Animasyonu**: Seçili çerçeve animasyonu
6. **Rozet Başarısı Bildirimi**: Yeni rozet açıldığında notification

---

## 📚 Kaynaklar
- Flask Documentation: https://flask.palletsprojects.com/
- SQLite Documentation: https://sqlite.org/docs.html
- HTML5 & CSS3: https://www.w3.org/

---

**Sistem Başarıyla Kuruldu! 🎉**
