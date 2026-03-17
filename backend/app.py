from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS

import jwt
import datetime

# 🔥 NUEVO: rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from validaciones import validar_registro, validar_login

app = Flask(__name__)
CORS(app)

# 🔥 CONFIG RATE LIMIT
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'pps.db')
JWT_SECRET = os.environ.get('JWT_SECRET', 'clave-super-secreta-pps-2024-abc123!')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# ─────────────────────────────────────────────
#  DB
# ─────────────────────────────────────────────
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
        cursor.execute(
            "INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)",
            ('Admin PPS', 'admin@pps.com', '000000000', admin_hash, 'admin')
        )
    conn.commit()
    conn.close()
    print("✅ DB OK. Admin: admin@pps.com / admin123")

# ─────────────────────────────────────────────
#  JWT HELPERS
# ─────────────────────────────────────────────
def generate_token(user_id: int, email: str, role: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'sub': str(user_id),
        'email': email,
        'role': role,
        'iat': now,
        'exp': now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": True},
        leeway=datetime.timedelta(seconds=10)
    )

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': 'Token inválido', 'detalle': str(e)}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Acceso denegado'}), 403
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
#  RUTAS
# ─────────────────────────────────────────────
@app.route('/')
def home():
    return jsonify({"message": "PPS Backend OK", "admin": "admin@pps.com / admin123"})


# 🔥 RATE LIMIT REGISTER
@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    data = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    phone    = data.get('phone', '').strip()
    password = data.get('password')

    if not all([name, email, phone, password]):
        return jsonify({'error': 'Faltan campos'}), 400
   
    errores = validar_registro(name, email, phone, password)
    if errores:
        return jsonify({'error': 'Datos inválidos', 'detalle': errores}), 422

    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, 'user')",
            (name, email, phone, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        token = generate_token(user_id, email, 'user')
        return jsonify({'message': 'Registrado OK', 'token': token}), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email existe'}), 409


# 🔥 RATE LIMIT LOGIN (CRÍTICO)
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data     = request.get_json()
    email    = data.get('email', '').strip()
    password = data.get('password')

    errores = validar_login(email, password)
    if errores:
        return jsonify({'error': 'Datos inválidos', 'detalle': errores}), 422

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password, role FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        token = generate_token(user[0], email, user[3])
        return jsonify({
            'message': 'Login OK',
            'user':  user[1],
            'role':  user[3],
            'token': token
        }), 200

    return jsonify({'error': 'Credenciales inválidas'}), 401


@app.route('/api/me', methods=['GET'])
@token_required
def me():
    return jsonify({'current_user': request.current_user}), 200


# 🔥 RATE LIMIT ADMIN
@app.route('/api/admin/users', methods=['GET'])
@limiter.limit("10 per minute")
@admin_required
def list_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = [{'id': r[0], 'name': r[1], 'email': r[2], 'phone': r[3], 'role': r[4]} for r in rows]
    return jsonify({'users': users}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)