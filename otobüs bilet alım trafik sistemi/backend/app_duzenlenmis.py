from flask import Flask, jsonify, request, make_response
import sqlite3
from flask_cors import CORS
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "otobusler.db")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'otobusler.db')
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

app = Flask(__name__, static_folder=os.path.join(PARENT_DIR, 'frontend'), static_url_path='/frontend')

CORS(app)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    hashed_password = hash_password(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                       (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    hashed_password = hash_password(password)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', 
                       (username, hashed_password))
        user = cursor.fetchone()
        return {"id": user["id"], "username": user["username"]} if user else None
    finally:
        conn.close()

def get_otobusler():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM otobusler')
        otobusler = cursor.fetchall()
        return [
            {
                "id": o["id"],
                "peron": f"{i+1}. Peron",
                "seferNo": f"SEF-{o['id']:03d}",
                "plaka": o["plaka"],
                "guzergah": o["guzergah"],
                "kalkis": "10:00",
                "fiyat": float(o["bilet_fiyati"] or 0),
                "trafik": "Orta",
                "sure": o["tahmini_sure"] or "45 dk",
                "koltuk": f"{int(float(str(o['doluluk_orani']).replace('%', '').strip()) * 50 / 100)}/50",
                "lat": 41.015,
                "lon": 28.979
            } for i, o in enumerate(otobusler)
        ]
    finally:
        conn.close()

def get_bilet_gecmisi(kullanici_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, o.guzergah 
            FROM biletler b
            JOIN otobusler o ON b.otobus_id = o.id
            WHERE b.kullanici_id = ?
            ORDER BY b.olusturulma_tarihi DESC
        ''', (kullanici_id,))
        return [
            {
                "id": row["id"],
                "otobus_plaka": row["otobus_plaka"],
                "guzergah": row["guzergah"],
                "nereden": row["nereden"],
                "nereye": row["nereye"],
                "tarih": row["tarih"],
                "saat": row["saat"],
                "koltuk_no": row["koltuk_no"],
                "fiyat": row["fiyat"],
                "durum": "Onaylandı" if row["durum"] else "İşlemde"
            } for row in cursor.fetchall()
        ]
    finally:
        conn.close()

def save_bilet(kullanici_id, otobus_id, otobus_plaka, nereden, nereye, tarih, saat, koltuk_no, fiyat):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO biletler (
                kullanici_id, otobus_id, otobus_plaka, nereden, nereye, 
                tarih, saat, koltuk_no, fiyat, durum, olusturulma_tarihi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kullanici_id, otobus_id, otobus_plaka, nereden, nereye,
            tarih, saat, koltuk_no, fiyat, True, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@app.route('/api/otobusler', methods=['GET'])
def otobusler():
    return jsonify(get_otobusler())

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"success": False, "message": "Tüm alanlar zorunludur"}), 400
    if register_user(data['username'], data['email'], data['password']):
        return jsonify({"success": True, "message": "Kayıt başarılı"})
    return jsonify({"success": False, "message": "Kullanıcı adı veya email kullanımda"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ['username', 'password']):
        return jsonify({"success": False, "message": "Kullanıcı adı ve şifre zorunludur"}), 400
    user = login_user(data['username'], data['password'])
    if user:
        return jsonify({"success": True, "message": "Giriş başarılı", "user": user})
    return jsonify({"success": False, "message": "Geçersiz bilgiler"}), 401

@app.route('/api/bilet-gecmisi', methods=['GET'])
def api_bilet_gecmisi():
    kullanici_id = request.args.get('kullanici_id')
    if not kullanici_id:
        return jsonify({"success": False, "message": "Kullanıcı ID gereklidir"}), 400
    try:
        return jsonify({"success": True, "biletler": get_bilet_gecmisi(kullanici_id)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/bilet-kaydet', methods=['POST'])
def api_bilet_kaydet():
    data = request.get_json()
    required_fields = [
        'kullanici_id', 'otobus_id', 'otobus_plaka', 
        'nereden', 'nereye', 'tarih', 'saat', 
        'koltuk_no', 'fiyat'
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Tüm alanlar zorunludur"}), 400
    try:
        bilet_id = save_bilet(
            kullanici_id=data['kullanici_id'],
            otobus_id=data['otobus_id'],
            otobus_plaka=data['otobus_plaka'],
            nereden=data['nereden'],
            nereye=data['nereye'],
            tarih=data['tarih'],
            saat=data['saat'],
            koltuk_no=data['koltuk_no'],
            fiyat=data['fiyat']
        )
        return jsonify({
            "success": True,
            "message": "Bilet kaydedildi",
            "bilet_id": bilet_id
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Bilet kaydedilemedi: {str(e)}"
        }), 500

@app.route('/debug-db')
def debug_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    result = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]});")
        result[table[0]] = cursor.fetchall()
    conn.close()
    return jsonify(result)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otobusler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plaka TEXT NOT NULL,
            guzergah TEXT NOT NULL,
            tahmini_sure TEXT,
            bilet_fiyati REAL,
            doluluk_orani REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS biletler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER NOT NULL,
            otobus_id INTEGER NOT NULL,
            otobus_plaka TEXT NOT NULL,
            nereden TEXT NOT NULL,
            nereye TEXT NOT NULL,
            tarih TEXT NOT NULL,
            saat TEXT NOT NULL,
            koltuk_no INTEGER NOT NULL,
            fiyat REAL NOT NULL,
            durum BOOLEAN NOT NULL,
            olusturulma_tarihi TEXT NOT NULL,
            FOREIGN KEY (kullanici_id) REFERENCES users(id),
            FOREIGN KEY (otobus_id) REFERENCES otobusler(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)