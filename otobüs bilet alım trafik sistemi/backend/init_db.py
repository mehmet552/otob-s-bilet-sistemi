import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'otobusler.db')

conn = sqlite3.connect(DB_PATH)
# Veritabanı dosyasının yolu

def initialize_database():
    # Her zaman backend klasörünü hedef al
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'otobusler.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    ...
import os

print("init_db.py dosyasının bulunduğu klasör:", os.path.abspath(os.path.dirname(__file__)))


import sqlite3

conn = sqlite3.connect("c:/Users/mehme/OneDrive/Masaüstü/havaist4/havaist4/havaist1/havaist1/backend/otobusler.db")
cursor = conn.cursor()

# Tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablolar = cursor.fetchall()

print("Veritabanındaki tablolar:")
for tablo in tablolar:
    print(tablo[0])

conn.close()
