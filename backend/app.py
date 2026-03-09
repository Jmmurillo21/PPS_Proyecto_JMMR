from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'pps.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    cursor.execute("SELECT id FROM users WHERE email='admin@pps.com'")
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)",
                      ('Admin PPS', 'admin@pps.com', '000000000', admin_hash, 'admin'))
    
    conn.commit()
    conn.close()
    print("✅ DB OK. Admin: admin@pps.com / admin123")

@app.route('/')
def home():
    return jsonify({"message": "PPS Backend OK", "admin": "admin@pps.com / admin123"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password')
    
    if not all([name, email, phone, password]):
        return jsonify({'error': 'Faltan campos'}), 400
    
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, 'user')",
                      (name, email, phone, password_hash))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Registrado OK'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email existe'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, password, role FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return jsonify({'message': 'Login OK', 'user': user[0], 'role': user[2]}), 200
    return jsonify({'error': 'Credenciales inválidas'}), 401

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
