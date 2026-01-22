from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge # Yeni hata yöneticisi için gerekli
import sqlite3
import os
import time
import hashlib
from datetime import datetime, timedelta

# --- Uygulama Ayarları ---
app = Flask(__name__)
app.secret_key = "gizli_bir_anahtar" # Burayı daha karmaşık bir şeyle değiştir!

# Online kullanıcı tracking (session'a koyacağız)
ONLINE_USERS = {}  # {user_id: last_activity_time}

# Forum kategorileri (sabit liste)
CATEGORIES = [
    "Matematik",
    "Fen / Biyoloji / Kimya / Fizik",
    "Türkçe & Edebiyat",
    "Yabancı Dil",
    "Sınav – TYT/AYT/Deneme",
    "Ödev Yardım",
    "Notlar & Özetler",
    "PDF / Dosya Paylaşımı",
    "Faydalı Linkler",
    "Öneri & Geri Bildirim",
    "Hata Bildir"
]

TEACHER_APPROVAL_CODE = "12345"
DB_NAME = "forum.db"

# --- UPLOAD ayarları ---
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip", "txt"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# 16 MB limit (RequestEntityTooLarge hatası bu limiti aşınca tetiklenir)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 

def allowed_file(filename):
    """Dosya uzantısının izin verilenler listesinde olup olmadığını kontrol eder."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Hata Yönetimi: Dosya Boyutu Sınırı ---
@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    """Büyük dosya yükleme hatasını yakalar."""
    return "Hata: Yüklediğin dosya çok büyük (Maksimum 16MB).", 413

# --- DB oluştur ---
def init_db():
    """Veritabanı tablolarını oluşturur."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
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
    
    # topics tablosu (TÜM sütunlar)
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
    
    # Diğer tablolar (rozetler, çerçeveler, arka plan renkleri)
    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            icon_path TEXT,
            description TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            description TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS background_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            color_code TEXT,
            gradient_code TEXT,
            requirement INTEGER DEFAULT 0
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id INTEGER,
            badge_id INTEGER,
            PRIMARY KEY (user_id, badge_id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_frames (
            user_id INTEGER,
            frame_id INTEGER,
            PRIMARY KEY (user_id, frame_id)
        )
    """)
    
    conn.commit()
    conn.close()

# --- ANA SAYFA (Konu Ekleme ve Listeleme) ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_name' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form.get('title','').strip()
        category = request.form.get('category','').strip()
        content = request.form.get('content','').strip()
        author = session['user_name']
        
        # Anonim kontrolü
        is_anonymous = 1 if request.form.get('is_anonymous') else 0
        is_approved = 0 if is_anonymous else 1  # Anonim konular onay beklemesi gerekir
        
        # Hocalara Sor kontrolü
        ask_teachers = 1 if request.form.get('ask_teachers') else 0
        
        print(f"DEBUG: is_anonymous form value = {request.form.get('is_anonymous')}")
        print(f"DEBUG: ask_teachers form value = {request.form.get('ask_teachers')}")
        print(f"DEBUG: is_anonymous = {is_anonymous}, is_approved = {is_approved}, ask_teachers = {ask_teachers}")

        attachment_name = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name_part, ext = os.path.splitext(filename)
                # Dosya adını benzersiz yapma
                filename = f"{int(time.time())}_{name_part}{ext}" 
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)
                attachment_name = filename
                print(f"DEBUG: Dosya kaydedildi - {attachment_name}")
            else:
                print(f"DEBUG: Dosya yüklenmedi - filename: {file.filename if file else 'None'}, allowed: {allowed_file(file.filename) if file else 'N/A'}")
        else:
            print("DEBUG: Dosya alanı gelmedi")

        # Veritabanına kaydet
        print(f"DEBUG: Veritabanına kaydediliyor - attachment: {attachment_name}, is_anonymous: {is_anonymous}, ask_teachers: {ask_teachers}")
        c.execute("""INSERT INTO topics (title, category, content, author, attachment, is_anonymous, is_approved, ask_teachers) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
         (title, category, content, author, attachment_name, is_anonymous, is_approved, ask_teachers))
        conn.commit()
        conn.close()
        
        # ⭐ XP HESAPLA VE ROZETLER AÇILSIN
        calculate_user_xp(session['user_id'])
        unlock_badges_for_user(session['user_id'])
        unlock_frames_for_user(session['user_id'])
        
    # Yeni bağlantı aç (önceki POST işleminde kapatıldı)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Konuları listele (admin ise onaylı/onaysız tüm konuları göster, değilse sadece onaylı konuları)
    if session.get('user_role') == 'admin':
        c.execute("SELECT * FROM topics ORDER BY id DESC")
    else:
        c.execute("SELECT * FROM topics WHERE is_approved=1 ORDER BY id DESC")
    topics = c.fetchall()
    
    # Her konu için cevap sayısını hesapla
    topics_with_reply_count = []
    for topic in topics:
        c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
        reply_count = c.fetchone()[0]
        topics_with_reply_count.append((*topic, reply_count))
    
    # Kullanıcı profil fotoğrafını al
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    user_photo = c.fetchone()
    user_profile_photo = user_photo[0] if user_photo else None
    
    conn.close()

    return render_template('index.html',
                           topics=topics_with_reply_count,
                           user_name=session.get('user_name'),
                           user_role=session.get('user_role'),
                           user_profile_photo=user_profile_photo)

# --- ARAMA ---
@app.route('/search', methods=['GET'])
def search_topics():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'newest')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # SQL sorgusu oluştur
    where_clauses = ["is_approved=1"]
    params = []
    
    # Arama sorgusu ekle (başlık ve içerikte ara)
    if search_query:
        where_clauses.append("(title LIKE ? OR content LIKE ?)")
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern])
    
    # Kategori filtresi ekle
    if category_filter:
        where_clauses.append("category = ?")
        params.append(category_filter)
    
    # Admin ise onay bekleyenleri de göster
    if session.get('user_role') == 'admin':
        where_clauses[0] = "1=1"  # Tüm konuları göster
    
    where_clause = " AND ".join(where_clauses)
    
    # Sıralama
    order_by = "id DESC"
    if sort_by == "oldest":
        order_by = "id ASC"
    elif sort_by == "most_replies":
        # Cevap sayısına göre sırala
        query = f"""
            SELECT t.*, COUNT(r.id) as reply_count
            FROM topics t
            LEFT JOIN replies r ON t.id = r.topic_id
            WHERE {where_clause}
            GROUP BY t.id
            ORDER BY reply_count DESC, t.id DESC
        """
        c.execute(query, params)
    else:
        query = f"SELECT * FROM topics WHERE {where_clause} ORDER BY {order_by}"
        c.execute(query, params)
    
    topics = c.fetchall()
    
    # Her konu için cevap sayısını hesapla
    topics_with_reply_count = []
    for topic in topics:
        c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
        reply_count = c.fetchone()[0]
        topics_with_reply_count.append((*topic, reply_count))
    
    # Kullanıcı profil fotoğrafını al
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    user_photo = c.fetchone()
    user_profile_photo = user_photo[0] if user_photo else None
    
    conn.close()
    
    return render_template('search_results.html',
                           topics=topics_with_reply_count,
                           user_name=session.get('user_name'),
                           user_role=session.get('user_role'),
                           user_profile_photo=user_profile_photo,
                           search_query=search_query,
                           category_filter=category_filter,
                           sort_by=sort_by)

# --- KONUYU GÖRÜNTÜLE (DÜZELTİLMİŞ) ---
@app.route('/topic/<int:topic_id>')
def show_topic(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Topics tablosunun sütunlarını adla al
    c.row_factory = sqlite3.Row
    
    c.execute("SELECT * FROM topics WHERE id=?", (topic_id,))
    topic = c.fetchone()
    
    if topic is None:
        conn.close()
        return "Konu Bulunamadı", 404
    
    # Şimdi güvenli bir şekilde 'approved' sütununa erişebiliriz
    # NOT: Eğer 'approved' sütunu yoksa, veritabanında oluştur
    try:
        is_approved = topic['approved']  # Sütun adıyla erişim
    except (KeyError, IndexError):
        # Eğer 'approved' sütunu yoksa, varsayılan olarak approved say
        is_approved = 1
    
    # Onaylanmamış konuyu sadece admin görebilir
    if is_approved == 0 and session.get('user_role') != 'admin':
        conn.close()
        return "Bu konu henüz onaya sunulmamıştır", 403
    
    # Cevapları al
    c.execute("SELECT * FROM replies WHERE topic_id=? ORDER BY id", (topic_id,))
    replies = c.fetchall()
    
    # Cevaplayan kişilerin profil fotoğraflarını al
    replies_with_photos = []
    for reply in replies:
        author = reply['author'] if isinstance(reply, sqlite3.Row) else reply[3]
        c.execute("SELECT profile_photo FROM users WHERE name=?", (author,))
        photo_result = c.fetchone()
        photo = photo_result[0] if photo_result else None
        
        # Tuple'a dönüştür ve photo ekle
        reply_tuple = tuple(reply) if isinstance(reply, sqlite3.Row) else reply
        replies_with_photos.append((*reply_tuple, photo))
    
    # Kullanıcı profil fotoğrafını al
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    user_photo = c.fetchone()
    user_profile_photo = user_photo[0] if user_photo else None
    
    conn.close()
    
    return render_template('topic.html',
                         topic=topic,
                         replies=replies_with_photos,
                         user_name=session.get('user_name'),
                         user_role=session.get('user_role'),
                         user_profile_photo=user_profile_photo)
# --- CEVAP EKLEME ---
@app.route('/reply/<int:topic_id>', methods=['POST'])
def reply(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))

    content = request.form.get('content','').strip()
    author = session['user_name']

    attachment_name = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name_part, ext = os.path.splitext(filename)
            # Dosya adını benzersiz yapma
            filename = f"{int(time.time())}_{name_part}{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            attachment_name = filename

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO replies (topic_id, content, author, attachment) VALUES (?, ?, ?, ?)",
     (topic_id, content, author, attachment_name))
    conn.commit()
    conn.close()

    # ⭐ XP HESAPLA VE ROZETLER AÇILSIN
    calculate_user_xp(session['user_id'])
    unlock_badges_for_user(session['user_id'])
    unlock_frames_for_user(session['user_id'])

    return redirect(url_for('show_topic', topic_id=topic_id))

# --- UPLOAD SERVE (Dosyayı Yayınlama) ---
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Kullanıcının yüklediği dosyaları güvenli bir şekilde sunar."""
    # Güvenlik için izin kontrolü eklenebilir, ancak send_from_directory zaten güvenlidir.
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --- DASHBOARD, REGISTER, LOGIN, LOGOUT, DELETE_TOPIC gibi diğer metotlar (değişmedi) ---

@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    # Kullanıcı bilgilerini veritabanından al
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, email, password, role, bio, profile_photo FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if user:
        return render_template('dashboard.html',
                               user_name=user[1],
                               user_email=user[2],
                               user_role=user[4],
                               user_bio=user[5],
                               user_profile_photo=user[6])
    else:
        return redirect(url_for('logout'))

@app.route('/profile/<user_name>')
def view_profile(user_name):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    # Öğrenci/Öğretmen adına göre profili göster
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT id, name, email, role, bio, profile_photo, 
               selected_frame_id, selected_badge_id, selected_bg_color_id
        FROM users WHERE name=?
    """, (user_name,))
    user = c.fetchone()
    
    # Frame bilgileri
    frame_color = "#333"
    if user and user[6]:  # selected_frame_id
        c.execute("SELECT description FROM frames WHERE id=?", (user[6],))
        frame_data = c.fetchone()
        if frame_data:
            desc = frame_data[0].lower()
            if "altın" in desc:
                frame_color = "#FFD700"
            elif "elmas" in desc:
                frame_color = "#00CED1"
            elif "neon" in desc:
                frame_color = "#39FF14"
            elif "başarı" in desc:
                frame_color = "#FF6347"
    
    # Badge bilgileri
    badge_icon = None
    if user and user[7]:  # selected_badge_id
        c.execute("SELECT icon_path FROM badges WHERE id=?", (user[7],))
        badge_data = c.fetchone()
        if badge_data:
            badge_icon = badge_data[0]
    
    # Background color
    bg_color = None
    text_color = "#000000"  # Default: siyah yazı
    if user and user[8]:  # selected_bg_color_id
        c.execute("SELECT gradient_code, color_code FROM background_colors WHERE id=?", (user[8],))
        color_data = c.fetchone()
        if color_data:
            bg_color = color_data[0] if color_data[0] else color_data[1]
            # Koyu arka plan ise beyaz yazı
            if bg_color and any(dark_color in bg_color.upper() for dark_color in ['#232323', '#2A2A2A', '#333333', '#1A1A1A', '#000000']):
                text_color = "#FFFFFF"
    
    conn.close()
    
    if not user:
        return "Kullanıcı Bulunamadı", 404
    
    # Geçerli kullanıcının profil fotoğrafı
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    current_user_photo = c.fetchone()
    conn.close()
    current_user_profile_photo = current_user_photo[0] if current_user_photo else None
    
    return render_template('profile.html',
                           viewed_user_name=user[1],
                           viewed_user_email=user[2],
                           viewed_user_role=user[3],
                           viewed_user_bio=user[4],
                           viewed_user_profile_photo=user[5],
                           viewed_user_frame_color=frame_color,
                           viewed_user_badge_icon=badge_icon,
                           viewed_user_bg_color=bg_color,
                           viewed_user_text_color=text_color,
                           user_name=session.get('user_name'),
                           user_role=session.get('user_role'),
                           user_profile_photo=current_user_profile_photo)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        role = request.form.get('role','student')
        teacher_code = request.form.get('teacher_code','')

        if role == "teacher" and teacher_code != TEACHER_APPROVAL_CODE:
            return "Geçersiz öğretmen onay kodu!"

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
             (name, email, password, role))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Bu e-posta zaten kullanılmış!"
        conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        password = request.form.get('password','').strip()
        
        # Şifreyi hash'le
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[4]
            return redirect(url_for('home'))
        else:
            return "Email veya şifre yanlış!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    bio = request.form.get('bio', '').strip()
    
    # Bio karakterini sınırla
    if len(bio) > 500:
        bio = bio[:500]
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Profil fotoğrafı yükleme işlemi
    profile_photo_name = None
    if 'profile_photo' in request.files:
        file = request.files['profile_photo']
        if file and file.filename != "" and allowed_file(file.filename):
            # Dosya boyutu kontrolü (5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > 5 * 1024 * 1024:
                return "Hata: Profil fotoğrafı 5MB'dan büyük olamaz!", 400
            
            filename = secure_filename(file.filename)
            name_part, ext = os.path.splitext(filename)
            filename = f"profile_{session['user_id']}_{int(time.time())}{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            profile_photo_name = filename
            
            # Eski profil fotoğrafını sil
            c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
            old_photo = c.fetchone()
            if old_photo and old_photo[0]:
                try:
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], old_photo[0]))
                except Exception:
                    pass
    
    # Profili güncelle
    if profile_photo_name:
        c.execute("UPDATE users SET name=?, bio=?, profile_photo=? WHERE id=?",
                  (name, bio, profile_photo_name, session['user_id']))
    else:
        c.execute("UPDATE users SET name=?, bio=? WHERE id=?",
                  (name, bio, session['user_id']))
    
    # Session'da adı güncelle
    session['user_name'] = name
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/delete_topic/<int:topic_id>')
def delete_topic(topic_id):
    if session.get('user_role') != 'admin':
        return "Yetkiniz yok!"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Ana konu ekini sil
    c.execute("SELECT attachment FROM topics WHERE id=?", (topic_id,))
    row = c.fetchone()
    if row and row[0]:
        try:
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], row[0]))
        except Exception:
            pass
            
    # Cevap eklerini sil
    c.execute("SELECT attachment FROM replies WHERE topic_id=?", (topic_id,))
    for r in c.fetchall():
        if r[0]:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], r[0]))
            except:
                pass
                
    # Veritabanından sil
    c.execute("DELETE FROM replies WHERE topic_id=?", (topic_id,))
    c.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# --- ADMIN PANELİ ---
@app.route('/admin-panel')
def admin_panel():
    # Debug
    print(f"DEBUG: Session user_role = {session.get('user_role')}")
    print(f"DEBUG: Session keys = {list(session.keys())}")
    print(f"DEBUG: Full session = {dict(session)}")
    
    if session.get('user_role') != 'admin':
        return f"Yetkiniz yok! Role: {session.get('user_role')}", 403
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Onay beklenen konuları getir
    c.execute("""
        SELECT id, title, category, content, author, is_anonymous, is_approved 
        FROM topics 
        WHERE is_approved=0 
        ORDER BY id DESC
    """)
    pending_topics = c.fetchall()
    
    # Admin kullanıcısının profil fotoğrafı
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    user_photo = c.fetchone()
    conn.close()
    user_profile_photo = user_photo[0] if user_photo else None
    
    return render_template('admin_panel.html',
                           pending_topics=pending_topics,
                           user_name=session['user_name'],
                           user_profile_photo=user_profile_photo)

@app.route('/approve-topic/<int:topic_id>/<action>')
def approve_topic(topic_id, action):
    if session.get('user_role') != 'admin':
        return "Yetkiniz yok!", 403
    
    if action not in ['approve', 'reject']:
        return "Geçersiz işlem!", 400
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if action == 'approve':
        c.execute("UPDATE topics SET is_approved=1 WHERE id=?", (topic_id,))
    elif action == 'reject':
        # Dosyalarını sil ve konuyu sil
        c.execute("SELECT attachment FROM topics WHERE id=?", (topic_id,))
        row = c.fetchone()
        if row and row[0]:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], row[0]))
            except Exception:
                pass
        
        # Cevapları ve eklerini sil
        c.execute("SELECT attachment FROM replies WHERE topic_id=?", (topic_id,))
        for r in c.fetchall():
            if r[0]:
                try:
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], r[0]))
                except:
                    pass
        
        c.execute("DELETE FROM replies WHERE topic_id=?", (topic_id,))
        c.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# --- KONUYU ÇÖZÜLDÜ OLARAK İŞARETLE ---
@app.route('/mark-solved/<int:topic_id>')
def mark_solved(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Konuyu getir
    c.execute("SELECT * FROM topics WHERE id=?", (topic_id,))
    topic = c.fetchone()
    
    if not topic:
        conn.close()
        return "Konu Bulunamadı", 404
    
    # Sadece konuyu açan kişi işaretleyebilir
    if topic[4] != session['user_name']:
        conn.close()
        return "Yalnızca konu sahibi bunu yapabilir!", 403
    
    # Çözüldü durumunu tersine çevir
    new_solved_status = 1 if topic[5] == 0 else 0
    c.execute("UPDATE topics SET solved=? WHERE id=?", (new_solved_status, topic_id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('show_topic', topic_id=topic_id))

# --- SON HARF OYUNU ---
WORD_GAME_MESSAGES = []  # Oyun mesajları

@app.route('/word-game')
def word_game():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    # Kullanıcı profil fotoğrafını al
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
    user_photo = c.fetchone()
    conn.close()
    user_profile_photo = user_photo[0] if user_photo else None
    
    # Online kullanıcı sayısını güncelle
    update_online_users(session['user_id'], session['user_name'])
    
    return render_template('word_game.html',
                           user_name=session.get('user_name'),
                           user_role=session.get('user_role'),
                           user_profile_photo=user_profile_photo)

@app.route('/api/word-game/messages')
def get_game_messages():
    """Oyun mesajlarını JSON olarak döndür"""
    if 'user_name' not in session:
        return jsonify([])
    return jsonify(WORD_GAME_MESSAGES)

@app.route('/api/word-game/submit-word', methods=['POST'])
def submit_word():
    """Yeni kelime gönder"""
    if 'user_name' not in session:
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    
    if not word:
        return jsonify({'error': 'Kelime boş olamaz'}), 400
    
    if len(word) < 2:
        return jsonify({'error': 'Kelime en az 2 harfli olmalı'}), 400
    
    # Tekrar kontrolü
    for msg in WORD_GAME_MESSAGES:
        if msg['word'] == word:
            return jsonify({'error': f'"{word}" kelimesi zaten kullanıldı!'}), 400
    
    # Son harf kontrolü
    if WORD_GAME_MESSAGES:
        last_word = WORD_GAME_MESSAGES[-1]['word']
        if last_word and last_word[-1] != word[0]:
            return jsonify({'error': f'Kelime "{last_word}" kelimesinin son harfi "{last_word[-1]}" ile başlamalı!'}), 400
    
    # Mesaj ekle
    message = {
        'user': session['user_name'],
        'word': word,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    WORD_GAME_MESSAGES.append(message)
    
    # Online kullanıcı güncelle
    update_online_users(session['user_id'], session['user_name'])
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/online-count')
def get_online_count():
    """Online kullanıcı sayısını döndür"""
    clean_offline_users()
    return jsonify({'count': len(ONLINE_USERS)})

def update_online_users(user_id, user_name):
    """Kullanıcıyı online olarak işaretle"""
    ONLINE_USERS[user_id] = {
        'name': user_name,
        'last_activity': datetime.now()
    }

def clean_offline_users():
    """15 dakikadır inaktif olan kullanıcıları çevrimdışı yap"""
    now = datetime.now()
    offline_users = [
        uid for uid, data in ONLINE_USERS.items()
        if (now - data['last_activity']).seconds > 900  # 15 dakika
    ]
    for uid in offline_users:
        del ONLINE_USERS[uid]

# --- KATEGORILER API ---
@app.route('/api/categories')
def get_categories():
    """Forum kategorilerini döndür (sabit liste)"""
    if 'user_name' not in session:
        return jsonify([])
    
    return jsonify(CATEGORIES)
@app.route('/api/topics/by-category/<category>')
def get_topics_by_category(category):
    """Belirli kategorideki konuları döndür"""
    if 'user_name' not in session:
        return jsonify([]), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Admin ise onaylı/onaysız tüm konuları, değilse sadece onaylı konuları getir
    if session.get('user_role') == 'admin':
        c.execute("SELECT * FROM topics WHERE category=? ORDER BY id DESC", (category,))
    else:
        c.execute("SELECT * FROM topics WHERE category=? AND is_approved=1 ORDER BY id DESC", (category,))
    
    topics = c.fetchall()
    
    # Her konu için cevap sayısını hesapla
    topics_with_reply_count = []
    for topic in topics:
        c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
        reply_count = c.fetchone()[0]
        topics_with_reply_count.append((*topic, reply_count))
    
    conn.close()
    
    # JSON formatında döndür
    result = []
    for topic in topics_with_reply_count:
        result.append({
            'id': topic[0],
            'title': topic[1],
            'category': topic[2],
            'content': topic[3],
            'author': topic[4],
            'solved': topic[5] if len(topic) > 5 else 0,
            'is_anonymous': topic[9] if len(topic) > 9 else 0,
            'is_approved': topic[10] if len(topic) > 10 else 1,
            'ask_teachers': topic[11] if len(topic) > 11 else 0,
            'reply_count': topic[-1]
        })
    
    return jsonify(result)
# === PROFIL ÖZELLEŞTİRME SİSTEMİ ===

def calculate_user_xp(user_id):
    """Kullanıcının toplam XP'sini hesapla (konu + cevaplardan)"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # User ID'den username'i al
    c.execute("SELECT name FROM users WHERE id=?", (user_id,))
    user_result = c.fetchone()
    if not user_result:
        conn.close()
        return 0
    username = user_result[0]
    
    # Her konu için 10 XP (username ile sorgu)
    c.execute("SELECT COUNT(*) FROM topics WHERE author=?", (username,))
    topic_count = c.fetchone()[0]
    
    # Her cevap için 5 XP (username ile sorgu)
    c.execute("SELECT COUNT(*) FROM replies WHERE author=?", (username,))
    reply_count = c.fetchone()[0]
    
    total_xp = (topic_count * 10) + (reply_count * 5)
    
    # XP'yi veritabanında güncelle
    c.execute("UPDATE users SET xp=? WHERE id=?", (total_xp, user_id))
    conn.commit()
    conn.close()
    
    print(f"DEBUG: XP={total_xp} (Topics:{topic_count}*10 + Replies:{reply_count}*5)")
    return total_xp

def unlock_badges_for_user(user_id):
    """Kullanıcının XP'sine göre otomatik rozetleri aç"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kullanıcının mevcut XP'sini al
    c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return
    
    user_xp = result[0]
    
    # XP'ye göre tüm açılabilir rozetleri bul
    c.execute("SELECT id FROM badges WHERE requirement <= ?", (user_xp,))
    available_badges = c.fetchall()
    
    # Henüz açılmamış rozetleri aç
    for badge_id in available_badges:
        try:
            c.execute("INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)",
                     (user_id, badge_id[0]))
        except sqlite3.IntegrityError:
            # Zaten açılmışsa ignore et
            pass
    
    conn.commit()
    conn.close()

def unlock_frames_for_user(user_id):
    """Kullanıcının XP'sine göre otomatik çerçeveleri aç"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return
    
    user_xp = result[0]
    
    c.execute("SELECT id FROM frames WHERE requirement <= ?", (user_xp,))
    available_frames = c.fetchall()
    
    for frame_id in available_frames:
        try:
            c.execute("INSERT INTO user_frames (user_id, frame_id) VALUES (?, ?)",
                     (user_id, frame_id[0]))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# --- Profil Özelleştirme API Endpoints ---

@app.route('/api/profile/<int:user_id>')
def get_user_profile_data(user_id):
    """Kullanıcının profil verilerini döndür (mini profil kartı için)"""
    if 'user_name' not in session:
        return jsonify({}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kullanıcı bilgilerini al
    c.execute("""
        SELECT id, name, bio, profile_photo, xp, role, selected_frame_id, 
               selected_badge_id, selected_bg_color_id
        FROM users WHERE id=?
    """, (user_id,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return jsonify({}), 404
    
    # Seçili çerçeve bilgisi
    frame_info = None
    if user[6]:  # selected_frame_id
        c.execute("SELECT id, name, image_path FROM frames WHERE id=?", (user[6],))
        frame = c.fetchone()
        if frame:
            frame_info = {"id": frame[0], "name": frame[1], "image": frame[2]}
    
    # Seçili rozet bilgisi
    badge_info = None
    if user[7]:  # selected_badge_id
        c.execute("SELECT id, name, icon_path FROM badges WHERE id=?", (user[7],))
        badge = c.fetchone()
        if badge:
            badge_info = {"id": badge[0], "name": badge[1], "icon": badge[2]}
    
    # Seçili arka plan bilgisi
    bg_info = None
    if user[8]:  # selected_bg_color_id
        c.execute("SELECT id, color_code, gradient_code FROM background_colors WHERE id=?", (user[8],))
        bg = c.fetchone()
        if bg:
            bg_info = {"id": bg[0], "color": bg[1], "gradient": bg[2]}
    
    # Kullanıcının tüm rozetlerini al
    c.execute("""
        SELECT b.id, b.name, b.icon_path FROM badges b
        JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id=?
    """, (user_id,))
    all_badges = c.fetchall()
    badges_list = [{"id": b[0], "name": b[1], "icon": b[2]} for b in all_badges]
    
    conn.close()
    
    return jsonify({
        "id": user[0],
        "name": user[1],
        "bio": user[2],
        "profile_photo": user[3],
        "xp": user[4],
        "role": user[5],
        "selected_frame": frame_info,
        "selected_badge": badge_info,
        "selected_bg_color": bg_info,
        "all_badges": badges_list
    })

@app.route('/api/profile/customize', methods=['POST'])
def customize_profile():
    """Profil özelleştirmesini kaydet"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    user_id = session['user_id']
    
    # Seçili çerçeve
    if 'frame_id' in data:
        frame_id = data['frame_id']
        c.execute("UPDATE users SET selected_frame_id=? WHERE id=?", (frame_id, user_id))
    
    # Seçili rozet
    if 'badge_id' in data:
        badge_id = data['badge_id']
        c.execute("UPDATE users SET selected_badge_id=? WHERE id=?", (badge_id, user_id))
    
    # Seçili arka plan rengi
    if 'bg_color_id' in data:
        bg_color_id = data['bg_color_id']
        c.execute("UPDATE users SET selected_bg_color_id=? WHERE id=?", (bg_color_id, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/profile/frames')
def get_user_frames():
    """Kullanıcının açtığı çerçeveleri döndür"""
    if 'user_id' not in session:
        return jsonify([]), 401
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kullanıcının XP'sini al
    c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    user_xp = result[0] if result else 0
    
    # XP'ye göre açılabilir çerçeveleri getir
    c.execute("""
        SELECT DISTINCT f.id, f.name, f.image_path, f.requirement, f.description
        FROM frames f
        WHERE f.requirement <= ?
        ORDER BY f.requirement
    """, (user_xp,))
    
    frames = c.fetchall()
    conn.close()
    
    result = []
    for f in frames:
        # Çerçevenin rengi - description'ından çıkart veya default
        color = "#333"  # default
        if f[4] and "altın" in f[4].lower():
            color = "#FFD700"
        elif f[4] and "elmas" in f[4].lower():
            color = "#00CED1"
        elif f[4] and "neon" in f[4].lower():
            color = "#39FF14"
        
        result.append({
            "id": f[0],
            "name": f[1],
            "image": f[2],
            "xp_required": f[3],
            "color": color
        })
    
    return jsonify(result)

@app.route('/api/profile/badges')
def get_user_badges():
    """Kullanıcının açtığı rozetleri döndür"""
    if 'user_id' not in session:
        return jsonify([]), 401
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kullanıcının XP'sini al
    c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    user_xp = result[0] if result else 0
    
    # XP'ye göre açılabilir rozetleri getir
    c.execute("""
        SELECT DISTINCT b.id, b.name, b.icon_path, b.description, b.requirement
        FROM badges b
        WHERE b.requirement <= ?
        ORDER BY b.requirement
    """, (user_xp,))
    
    badges = c.fetchall()
    conn.close()
    
    result = [{"id": b[0], "name": b[1], "icon": b[2], "description": b[3], "xp_required": b[4]} for b in badges]
    return jsonify(result)

@app.route('/api/profile/bg-colors')
def get_bg_colors():
    """Kullanıcının açtığı arka plan renklerini döndür"""
    if 'user_id' not in session:
        return jsonify([]), 401
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Kullanıcının XP'sini al
    c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    user_xp = result[0] if result else 0
    
    # XP'ye göre açılabilir arka planları getir
    c.execute("""
        SELECT id, name, color_code, gradient_code, requirement
        FROM background_colors
        WHERE requirement <= ?
        ORDER BY requirement
    """, (user_xp,))
    
    colors = c.fetchall()
    conn.close()
    
    result = [{"id": c[0], "name": c[1], "color_code": c[2], "gradient_code": c[3], "requirement": c[4]} for c in colors]
    return jsonify(result)

@app.route('/api/user-widget/<user_name>')
def get_user_widget(user_name):
    """Konu listesi ve cevapların yanında gösterilecek küçük profil widget'ı"""
    if 'user_name' not in session:
        return jsonify({}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, name, profile_photo, role, xp, selected_frame_id, selected_badge_id
        FROM users WHERE name=?
    """, (user_name,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return jsonify({}), 404
    
    # Çerçeve bilgisi
    frame_image = None
    if user[5]:  # selected_frame_id
        c.execute("SELECT image_path FROM frames WHERE id=?", (user[5],))
        frame = c.fetchone()
        if frame:
            frame_image = frame[0]
    
    # Rozet bilgisi
    badge_icon = None
    if user[6]:  # selected_badge_id
        c.execute("SELECT icon_path FROM badges WHERE id=?", (user[6],))
        badge = c.fetchone()
        if badge:
            badge_icon = badge[0]
    
    conn.close()
    
    return jsonify({
        "id": user[0],
        "name": user[1],
        "profile_photo": user[2],
        "role": user[3],
        "xp": user[4],
        "frame_image": frame_image,
        "badge_icon": badge_icon
    })



#if __name__ == '__main__':
    # init_db'nin ilk çalışmada çalıştığından emin olmak için buraya da koyabiliriz.
#    init_db() 
#    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
