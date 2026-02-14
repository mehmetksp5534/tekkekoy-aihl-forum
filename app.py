from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import sqlite3
import os
import time
import hashlib
from datetime import datetime, timedelta

# --- Uygulama Ayarları ---
app = Flask(__name__)
app.secret_key = "gizli_bir_anahtar_2024_super_secret_key_12345"

# Online kullanıcı tracking
ONLINE_USERS = {}

# Forum kategorileri
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
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

def allowed_file(filename):
    """Dosya uzantısının izin verilenler listesinde olup olmadığını kontrol eder."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Hata Yönetimi ---
@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    """Büyük dosya yükleme hatasını yakalar."""
    return "Hata: Yüklediğin dosya çok büyük (Maksimum 16MB).", 413

# --- SQLite Ayarları ---
def init_sqlite():
    """SQLite performans ayarları"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        conn.close()
    except Exception as e:
        print(f"SQLite init error: {e}")
        if conn:
            conn.close()

# --- DB oluştur ---
def init_db():
    """Veritabanı tablolarını oluşturur."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        
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
                selected_bg_color_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                night_mode INTEGER DEFAULT 0
            )
        """)
        
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
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                content TEXT,
                author TEXT,
                attachment TEXT
            )
        """)
        
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
    except Exception as e:
        print(f"Database init error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# === PROFIL ÖZELLEŞTİRME FONKSİYONLARI (ÖNCELİKLE TANIMLANMALI) ===

def calculate_user_xp(user_id):
    """Kullanıcının toplam XP'sini hesapla"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("SELECT name FROM users WHERE id=?", (user_id,))
        user_result = c.fetchone()
        if not user_result:
            return 0
        username = user_result[0]
        
        c.execute("SELECT COUNT(*) FROM topics WHERE author=?", (username,))
        topic_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM replies WHERE author=?", (username,))
        reply_count = c.fetchone()[0]
        
        total_xp = (topic_count * 10) + (reply_count * 5)
        
        c.execute("UPDATE users SET xp=? WHERE id=?", (total_xp, user_id))
        conn.commit()
        
        return total_xp
    
    except Exception as e:
        print(f"Calculate XP error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def unlock_badges_for_user(user_id):
    """Kullanıcının XP'sine göre rozetleri aç"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        if not result:
            return
        
        user_xp = result[0]
        
        c.execute("SELECT id FROM badges WHERE requirement <= ?", (user_xp,))
        available_badges = c.fetchall()
        
        for badge_id in available_badges:
            try:
                c.execute("INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)",
                         (user_id, badge_id[0]))
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
    
    except Exception as e:
        print(f"Unlock badges error: {e}")
    finally:
        if conn:
            conn.close()

def unlock_frames_for_user(user_id):
    """Kullanıcının XP'sine göre çerçeveleri aç"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        if not result:
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
    
    except Exception as e:
        print(f"Unlock frames error: {e}")
    finally:
        if conn:
            conn.close()

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
        if (now - data['last_activity']).seconds > 900
    ]
    for uid in offline_users:
        del ONLINE_USERS[uid]

# === ROUTE'LAR ===

# --- ANA SAYFA ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_name' not in session:
        return redirect(url_for('login'))

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            content = request.form.get('content', '').strip()
            author = session['user_name']
            
            is_anonymous = 1 if request.form.get('is_anonymous') else 0
            is_approved = 0 if is_anonymous else 1
            ask_teachers = 1 if request.form.get('ask_teachers') else 0

            attachment_name = None
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file and file.filename != "" and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    name_part, ext = os.path.splitext(filename)
                    filename = f"{int(time.time())}_{name_part}{ext}"
                    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(save_path)
                    attachment_name = filename

            c.execute("""INSERT INTO topics (title, category, content, author, attachment, is_anonymous, is_approved, ask_teachers) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, category, content, author, attachment_name, is_anonymous, is_approved, ask_teachers))
            conn.commit()
            
            calculate_user_xp(session['user_id'])
            unlock_badges_for_user(session['user_id'])
            unlock_frames_for_user(session['user_id'])
        
        if session.get('user_role') == 'admin':
            c.execute("SELECT * FROM topics ORDER BY id DESC")
        else:
            c.execute("SELECT * FROM topics WHERE is_approved=1 ORDER BY id DESC")
        topics = c.fetchall()
        
        topics_with_reply_count = []
        for topic in topics:
            c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
            reply_count = c.fetchone()[0]
            topics_with_reply_count.append((*topic, reply_count))
        
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        user_photo = c.fetchone()
        user_profile_photo = user_photo[0] if user_photo else None
        
        return render_template('index.html',
                               topics=topics_with_reply_count,
                               user_name=session.get('user_name'),
                               user_role=session.get('user_role'),
                               user_profile_photo=user_profile_photo)
    
    except Exception as e:
        print(f"Home error: {e}")
        if conn:
            conn.rollback()
        return f"Bir hata oluştu: {e}", 500
    finally:
        if conn:
            conn.close()

# --- ARAMA ---
@app.route('/search', methods=['GET'])
def search_topics():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'newest')
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        where_clauses = ["is_approved=1"]
        params = []
        
        if search_query:
            where_clauses.append("(title LIKE ? OR content LIKE ?)")
            search_pattern = f"%{search_query}%"
            params.extend([search_pattern, search_pattern])
        
        if category_filter:
            where_clauses.append("category = ?")
            params.append(category_filter)
        
        if session.get('user_role') == 'admin':
            where_clauses[0] = "1=1"
        
        where_clause = " AND ".join(where_clauses)
        
        order_by = "id DESC"
        if sort_by == "oldest":
            order_by = "id ASC"
        elif sort_by == "most_replies":
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
        
        topics_with_reply_count = []
        for topic in topics:
            c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
            reply_count = c.fetchone()[0]
            topics_with_reply_count.append((*topic, reply_count))
        
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        user_photo = c.fetchone()
        user_profile_photo = user_photo[0] if user_photo else None
        
        return render_template('search_results.html',
                               topics=topics_with_reply_count,
                               user_name=session.get('user_name'),
                               user_role=session.get('user_role'),
                               user_profile_photo=user_profile_photo,
                               search_query=search_query,
                               category_filter=category_filter,
                               sort_by=sort_by)
    
    except Exception as e:
        print(f"Search error: {e}")
        return f"Arama hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- KONUYU GÖRÜNTÜLE ---
@app.route('/topic/<int:topic_id>')
def show_topic(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        c.row_factory = sqlite3.Row
        
        c.execute("SELECT * FROM topics WHERE id=?", (topic_id,))
        topic = c.fetchone()
        
        if topic is None:
            return "Konu Bulunamadı", 404
        
        is_approved = topic['is_approved'] if 'is_approved' in topic.keys() else 1
        
        if is_approved == 0 and session.get('user_role') != 'admin':
            return "Bu konu henüz onaya sunulmamıştır", 403
        
        c.execute("SELECT * FROM replies WHERE topic_id=? ORDER BY id", (topic_id,))
        replies = c.fetchall()
        
        replies_with_photos = []
        for reply in replies:
            author = reply['author'] if isinstance(reply, sqlite3.Row) else reply[3]
            c.execute("SELECT profile_photo FROM users WHERE name=?", (author,))
            photo_result = c.fetchone()
            photo = photo_result[0] if photo_result else None
            
            reply_tuple = tuple(reply) if isinstance(reply, sqlite3.Row) else reply
            replies_with_photos.append((*reply_tuple, photo))
        
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        user_photo = c.fetchone()
        user_profile_photo = user_photo[0] if user_photo else None
        
        return render_template('topic.html',
                             topic=topic,
                             replies=replies_with_photos,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'),
                             user_profile_photo=user_profile_photo)
    
    except Exception as e:
        print(f"Show topic error: {e}")
        return f"Konu görüntüleme hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- CEVAP EKLEME ---
@app.route('/reply/<int:topic_id>', methods=['POST'])
def reply(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))

    content = request.form.get('content', '').strip()
    author = session['user_name']

    attachment_name = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name_part, ext = os.path.splitext(filename)
            filename = f"{int(time.time())}_{name_part}{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            attachment_name = filename

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        c.execute("INSERT INTO replies (topic_id, content, author, attachment) VALUES (?, ?, ?, ?)",
                 (topic_id, content, author, attachment_name))
        conn.commit()
        
        calculate_user_xp(session['user_id'])
        unlock_badges_for_user(session['user_id'])
        unlock_frames_for_user(session['user_id'])
        
    except Exception as e:
        print(f"Reply error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

    return redirect(url_for('show_topic', topic_id=topic_id))

# --- UPLOAD SERVE ---
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --- DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        c.execute("SELECT id, name, email, password, role, bio, profile_photo FROM users WHERE id=?", (session['user_id'],))
        user = c.fetchone()
        
        if user:
            return render_template('dashboard.html',
                                   user_name=user[1],
                                   user_email=user[2],
                                   user_role=user[4],
                                   user_bio=user[5],
                                   user_profile_photo=user[6])
        else:
            return redirect(url_for('logout'))
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        return f"Dashboard hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- PROFİL GÖRÜNTÜLE ---
@app.route('/profile/<user_name>')
def view_profile(user_name):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        c.execute("""
            SELECT id, name, email, role, bio, profile_photo, 
                   selected_frame_id, selected_badge_id, selected_bg_color_id
            FROM users WHERE name=?
        """, (user_name,))
        user = c.fetchone()
        
        if not user:
            return "Kullanıcı Bulunamadı", 404
        
        frame_color = "#333"
        if user[6]:
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
        
        badge_icon = None
        if user[7]:
            c.execute("SELECT icon_path FROM badges WHERE id=?", (user[7],))
            badge_data = c.fetchone()
            if badge_data:
                badge_icon = badge_data[0]
        
        bg_color = None
        text_color = "#000000"
        if user[8]:
            c.execute("SELECT gradient_code, color_code FROM background_colors WHERE id=?", (user[8],))
            color_data = c.fetchone()
            if color_data:
                bg_color = color_data[0] if color_data[0] else color_data[1]
                if bg_color and any(dark_color in bg_color.upper() for dark_color in ['#232323', '#2A2A2A', '#333333', '#1A1A1A', '#000000']):
                    text_color = "#FFFFFF"
        
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        current_user_photo = c.fetchone()
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
    
    except Exception as e:
        print(f"View profile error: {e}")
        return f"Profil görüntüleme hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- KAYIT OL ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        teacher_code = request.form.get('teacher_code', '')

        if role == "teacher" and teacher_code != TEACHER_APPROVAL_CODE:
            return "Geçersiz öğretmen onay kodu!"

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = None
        try:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                     (name, email, hashed_password, role))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Bu e-posta zaten kullanılmış!"
        except Exception as e:
            print(f"Register error: {e}")
            if conn:
                conn.rollback()
            return f"Kayıt hatası: {e}", 500
        finally:
            if conn:
                conn.close()
    
    return render_template('register.html')

# --- GİRİŞ YAP ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed_password))
            user = c.fetchone()
            
            if user:
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_role'] = user[4]
                return redirect(url_for('home'))
            else:
                return "Email veya şifre yanlış!"
        
        except Exception as e:
            print(f"Login error: {e}")
            return f"Giriş hatası: {e}", 500
        finally:
            if conn:
                conn.close()
    
    return render_template('login.html')

# --- ÇIKIŞ YAP ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- PROFİLİ DÜZENLE ---
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    bio = request.form.get('bio', '').strip()
    
    if len(bio) > 500:
        bio = bio[:500]
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        profile_photo_name = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != "" and allowed_file(file.filename):
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
                
                c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
                old_photo = c.fetchone()
                if old_photo and old_photo[0]:
                    try:
                        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], old_photo[0]))
                    except Exception:
                        pass
        
        if profile_photo_name:
            c.execute("UPDATE users SET name=?, bio=?, profile_photo=? WHERE id=?",
                      (name, bio, profile_photo_name, session['user_id']))
        else:
            c.execute("UPDATE users SET name=?, bio=? WHERE id=?",
                      (name, bio, session['user_id']))
        
        session['user_name'] = name
        conn.commit()
        
        return redirect(url_for('dashboard'))
    
    except sqlite3.OperationalError as e:
        print(f"Database locked error: {e}")
        if conn:
            conn.rollback()
        return "Veritabanı meşgul! Lütfen tekrar deneyin.", 500
    except Exception as e:
        print(f"Edit profile error: {e}")
        if conn:
            conn.rollback()
        return f"Profil güncelleme hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- KONU SİL ---
@app.route('/delete_topic/<int:topic_id>')
def delete_topic(topic_id):
    if session.get('user_role') != 'admin':
        return "Yetkiniz yok!"
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("SELECT attachment FROM topics WHERE id=?", (topic_id,))
        row = c.fetchone()
        if row and row[0]:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], row[0]))
            except Exception:
                pass
        
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
        
        return redirect(url_for('home'))
    
    except Exception as e:
        print(f"Delete topic error: {e}")
        if conn:
            conn.rollback()
        return f"Konu silme hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- ADMIN PANELİ ---
@app.route('/admin-panel')
def admin_panel():
    if session.get('user_role') != 'admin':
        return f"Yetkiniz yok! Role: {session.get('user_role')}", 403
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, title, category, content, author, is_anonymous, is_approved 
            FROM topics 
            WHERE is_approved=0 
            ORDER BY id DESC
        """)
        pending_topics = c.fetchall()
        
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        user_photo = c.fetchone()
        user_profile_photo = user_photo[0] if user_photo else None
        
        return render_template('admin_panel.html',
                               pending_topics=pending_topics,
                               user_name=session['user_name'],
                               user_profile_photo=user_profile_photo)
    
    except Exception as e:
        print(f"Admin panel error: {e}")
        return f"Admin panel hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- KONU ONAYLA/REDDET ---
@app.route('/approve-topic/<int:topic_id>/<action>')
def approve_topic(topic_id, action):
    if session.get('user_role') != 'admin':
        return "Yetkiniz yok!", 403
    
    if action not in ['approve', 'reject']:
        return "Geçersiz işlem!", 400
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        if action == 'approve':
            c.execute("UPDATE topics SET is_approved=1 WHERE id=?", (topic_id,))
        elif action == 'reject':
            c.execute("SELECT attachment FROM topics WHERE id=?", (topic_id,))
            row = c.fetchone()
            if row and row[0]:
                try:
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], row[0]))
                except Exception:
                    pass
            
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
        return redirect(url_for('admin_panel'))
    
    except Exception as e:
        print(f"Approve topic error: {e}")
        if conn:
            conn.rollback()
        return f"Onaylama hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- KONUYU ÇÖZÜLDÜ OLARAK İŞARETLE ---
@app.route('/mark-solved/<int:topic_id>')
def mark_solved(topic_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("SELECT * FROM topics WHERE id=?", (topic_id,))
        topic = c.fetchone()
        
        if not topic:
            return "Konu Bulunamadı", 404
        
        if topic[4] != session['user_name']:
            return "Yalnızca konu sahibi bunu yapabilir!", 403
        
        new_solved_status = 1 if topic[5] == 0 else 0
        c.execute("UPDATE topics SET solved=? WHERE id=?", (new_solved_status, topic_id))
        conn.commit()
        
        return redirect(url_for('show_topic', topic_id=topic_id))
    
    except Exception as e:
        print(f"Mark solved error: {e}")
        if conn:
            conn.rollback()
        return f"İşaretleme hatası: {e}", 500
    finally:
        if conn:
            conn.close()

# --- SON HARF OYUNU ---
WORD_GAME_MESSAGES = []

@app.route('/word-game')
def word_game():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        c.execute("SELECT profile_photo FROM users WHERE id=?", (session['user_id'],))
        user_photo = c.fetchone()
        user_profile_photo = user_photo[0] if user_photo else None
        
        update_online_users(session['user_id'], session['user_name'])
        
        return render_template('word_game.html',
                               user_name=session.get('user_name'),
                               user_role=session.get('user_role'),
                               user_profile_photo=user_profile_photo)
    
    except Exception as e:
        print(f"Word game error: {e}")
        return f"Oyun hatası: {e}", 500
    finally:
        if conn:
            conn.close()

@app.route('/api/word-game/messages')
def get_game_messages():
    if 'user_name' not in session:
        return jsonify([])
    return jsonify(WORD_GAME_MESSAGES)

@app.route('/api/word-game/submit-word', methods=['POST'])
def submit_word():
    if 'user_name' not in session:
        return jsonify({'error': 'Giriş gerekli'}), 401
    
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    
    if not word:
        return jsonify({'error': 'Kelime boş olamaz'}), 400
    
    if len(word) < 2:
        return jsonify({'error': 'Kelime en az 2 harfli olmalı'}), 400
    
    for msg in WORD_GAME_MESSAGES:
        if msg['word'] == word:
            return jsonify({'error': f'"{word}" kelimesi zaten kullanıldı!'}), 400
    
    if WORD_GAME_MESSAGES:
        last_word = WORD_GAME_MESSAGES[-1]['word']
        if last_word and last_word[-1] != word[0]:
            return jsonify({'error': f'Kelime "{last_word}" kelimesinin son harfi "{last_word[-1]}" ile başlamalı!'}), 400
    
    message = {
        'user': session['user_name'],
        'word': word,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    WORD_GAME_MESSAGES.append(message)
    
    update_online_users(session['user_id'], session['user_name'])
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/online-count')
def get_online_count():
    clean_offline_users()
    return jsonify({'count': len(ONLINE_USERS)})

# --- KATEGORİLER API ---
@app.route('/api/categories')
def get_categories():
    if 'user_name' not in session:
        return jsonify([])
    return jsonify(CATEGORIES)

@app.route('/api/topics/by-category/<category>')
def get_topics_by_category(category):
    if 'user_name' not in session:
        return jsonify([]), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        if session.get('user_role') == 'admin':
            c.execute("SELECT * FROM topics WHERE category=? ORDER BY id DESC", (category,))
        else:
            c.execute("SELECT * FROM topics WHERE category=? AND is_approved=1 ORDER BY id DESC", (category,))
        
        topics = c.fetchall()
        
        topics_with_reply_count = []
        for topic in topics:
            c.execute("SELECT COUNT(*) FROM replies WHERE topic_id=?", (topic[0],))
            reply_count = c.fetchone()[0]
            topics_with_reply_count.append((*topic, reply_count))
        
        result = []
        for topic in topics_with_reply_count:
            result.append({
                'id': topic[0],
                'title': topic[1],
                'category': topic[2],
                'content': topic[3],
                'author': topic[4],
                'solved': topic[5] if len(topic) > 5 else 0,
                'attachment': topic[6] if len(topic) > 6 else None,
                'is_anonymous': topic[7] if len(topic) > 7 else 0,
                'is_approved': topic[8] if len(topic) > 8 else 1,
                'ask_teachers': topic[9] if len(topic) > 9 else 0,
                'reply_count': topic[-1]
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Get topics by category error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- PROFİL API ENDPOINTS ---

@app.route('/api/profile/<int:user_id>')
def get_user_profile_data(user_id):
    if 'user_name' not in session:
        return jsonify({}), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, name, bio, profile_photo, xp, role, selected_frame_id, 
                   selected_badge_id, selected_bg_color_id
            FROM users WHERE id=?
        """, (user_id,))
        user = c.fetchone()
        
        if not user:
            return jsonify({}), 404
        
        frame_info = None
        if user[6]:
            c.execute("SELECT id, name, image_path FROM frames WHERE id=?", (user[6],))
            frame = c.fetchone()
            if frame:
                frame_info = {"id": frame[0], "name": frame[1], "image": frame[2]}
        
        badge_info = None
        if user[7]:
            c.execute("SELECT id, name, icon_path FROM badges WHERE id=?", (user[7],))
            badge = c.fetchone()
            if badge:
                badge_info = {"id": badge[0], "name": badge[1], "icon": badge[2]}
        
        bg_info = None
        if user[8]:
            c.execute("SELECT id, color_code, gradient_code FROM background_colors WHERE id=?", (user[8],))
            bg = c.fetchone()
            if bg:
                bg_info = {"id": bg[0], "color": bg[1], "gradient": bg[2]}
        
        c.execute("""
            SELECT b.id, b.name, b.icon_path FROM badges b
            JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id=?
        """, (user_id,))
        all_badges = c.fetchall()
        badges_list = [{"id": b[0], "name": b[1], "icon": b[2]} for b in all_badges]
        
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
    
    except Exception as e:
        print(f"Get profile data error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/profile/customize', methods=['POST'])
def customize_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        user_id = session['user_id']
        
        if 'frame_id' in data:
            c.execute("UPDATE users SET selected_frame_id=? WHERE id=?", (data['frame_id'], user_id))
        
        if 'badge_id' in data:
            c.execute("UPDATE users SET selected_badge_id=? WHERE id=?", (data['badge_id'], user_id))
        
        if 'bg_color_id' in data:
            c.execute("UPDATE users SET selected_bg_color_id=? WHERE id=?", (data['bg_color_id'], user_id))
        
        conn.commit()
        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Customize profile error: {e}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/profile/frames')
def get_user_frames():
    if 'user_id' not in session:
        return jsonify([]), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        user_id = session['user_id']
        
        c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        user_xp = result[0] if result else 0
        
        c.execute("""
            SELECT DISTINCT f.id, f.name, f.image_path, f.requirement, f.description
            FROM frames f
            WHERE f.requirement <= ?
            ORDER BY f.requirement
        """, (user_xp,))
        
        frames = c.fetchall()
        
        result = []
        for f in frames:
            color = "#333"
            if f[4]:
                desc = f[4].lower()
                if "altın" in desc:
                    color = "#FFD700"
                elif "elmas" in desc:
                    color = "#00CED1"
                elif "neon" in desc:
                    color = "#39FF14"
            
            result.append({
                "id": f[0],
                "name": f[1],
                "image": f[2],
                "xp_required": f[3],
                "color": color
            })
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Get frames error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/profile/badges')
def get_user_badges():
    if 'user_id' not in session:
        return jsonify([]), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        user_id = session['user_id']
        
        c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        user_xp = result[0] if result else 0
        
        c.execute("""
            SELECT DISTINCT b.id, b.name, b.icon_path, b.description, b.requirement
            FROM badges b
            WHERE b.requirement <= ?
            ORDER BY b.requirement
        """, (user_xp,))
        
        badges = c.fetchall()
        result = [{"id": b[0], "name": b[1], "icon": b[2], "description": b[3], "xp_required": b[4]} for b in badges]
        return jsonify(result)
    
    except Exception as e:
        print(f"Get badges error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/profile/bg-colors')
def get_bg_colors():
    if 'user_id' not in session:
        return jsonify([]), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        user_id = session['user_id']
        
        c.execute("SELECT xp FROM users WHERE id=?", (user_id,))
        result = c.fetchone()
        user_xp = result[0] if result else 0
        
        c.execute("""
            SELECT id, name, color_code, gradient_code, requirement
            FROM background_colors
            WHERE requirement <= ?
            ORDER BY requirement
        """, (user_xp,))
        
        colors = c.fetchall()
        result = [{"id": c[0], "name": c[1], "color_code": c[2], "gradient_code": c[3], "requirement": c[4]} for c in colors]
        return jsonify(result)
    
    except Exception as e:
        print(f"Get bg colors error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/user-widget/<user_name>')
def get_user_widget(user_name):
    if 'user_name' not in session:
        return jsonify({}), 401
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, name, profile_photo, role, xp, selected_frame_id, selected_badge_id
            FROM users WHERE name=?
        """, (user_name,))
        user = c.fetchone()
        
        if not user:
            return jsonify({}), 404
        
        frame_image = None
        if user[5]:
            c.execute("SELECT image_path FROM frames WHERE id=?", (user[5],))
            frame = c.fetchone()
            if frame:
                frame_image = frame[0]
        
        badge_icon = None
        if user[6]:
            c.execute("SELECT icon_path FROM badges WHERE id=?", (user[6],))
            badge = c.fetchone()
            if badge:
                badge_icon = badge[0]
        
        return jsonify({
            "id": user[0],
            "name": user[1],
            "profile_photo": user[2],
            "role": user[3],
            "xp": user[4],
            "frame_image": frame_image,
            "badge_icon": badge_icon
        })
    
    except Exception as e:
        print(f"Get user widget error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# === UYGULAMA BAŞLATMA ===

if __name__ == "__main__":
    init_sqlite()
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)