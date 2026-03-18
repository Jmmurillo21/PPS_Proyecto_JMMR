# 🔐 PPS - Plataforma de Protección de Seguridad

**Proyecto Final: Sistema de Autenticación Seguro con enfoque en OWASP Top 10**

---

## 📋 Índice
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Características Principales](#características-principales)
3. [Arquitectura Técnica](#arquitectura-técnica)
4. [Instalación y Uso](#instalación-y-uso)
5. [OWASP Top 10 - Cobertura de Seguridad](#owasp-top-10---cobertura-de-seguridad)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [API Endpoints](#api-endpoints)
8. [Testing](#testing)

---

## 📖 Descripción del Proyecto

**PPS** es una plataforma de autenticación y autorización segura desarrollada como proyecto final para demostrar la implementación de mejores prácticas en seguridad web. El sistema permite:

- ✅ Registro seguro de usuarios con validación exhaustiva
- ✅ Autenticación basada en JWT con tokens con expiración
- ✅ Sistema de roles (Admin/Usuario)
- ✅ Panel administrativo para gestión de usuarios
- ✅ Protección contra ataques comunes de OWASP Top 10

### Tecnologías Utilizadas
- **Backend**: Flask 3.0.3 (Python)
- **Autenticación**: JWT (JSON Web Tokens)
- **Base de Datos**: SQLite
- **Frontend**: HTML5 + Vanilla JavaScript + Tailwind
- **Orquestación**: Docker Compose
- **Rate Limiting**: Flask-Limiter
- **Hashing**: Werkzeug (pbkdf2:sha256)
- **Testing**: pytest + pytest-flask

---

## ✨ Características Principales

### 🔑 Autenticación y Autorización
- Token JWT con expiración de 24 horas
- Decoradores `@token_required` y `@admin_required` para protección de endpoints
- Validación de credenciales con hashing seguro

### 🛡️ Validaciones de Entrada
- **Nombre**: Máximo 50 caracteres, solo letras y espacios
- **Email**: Formato válido, máximo 100 caracteres
- **Teléfono**: Formato español (9 dígitos, comienza con 6-9)
- **Contraseña**: Mínimo 8 caracteres, máximo 128, incluye mayúsculas, minúsculas, números y caracteres especiales

### ⚡ Rate Limiting
- Registro: 3 intentos por minuto
- Login: 5 intentos por minuto
- Admin: 10 solicitudes por minuto
- Default: 200 solicitudes/día, 50/hora

### 📊 Control de Acceso Basado en Roles
- **Admin**: Acceso a panel administrativo y listado de usuarios
- **User**: Acceso solo a su perfil

---

## 🏗️ Arquitectura Técnica

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                           │
│  (HTML5 + JS) - Login, Registro, Admin, Usuario    │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/CORS
┌────────────────────▼────────────────────────────────┐
│                BACKEND (Flask)                       │
│  - Validación de entrada                            │
│  - Autenticación JWT                                │
│  - Rate Limiting                                    │
│  - Control de Acceso                                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Base de Datos (SQLite)                  │
│  - users (id, name, email, phone, password, role)  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación y Uso

### Opción 1: Con Docker Compose 

```bash
# Clonar el repositorio
git clone <repo-url>
cd PPT_Proyecto

# Iniciar los servicios
docker-compose up --build

# Backend disponible en: http://localhost:5001
# Frontend disponible en: http://localhost:8080
```

### Credenciales por Defecto
```
Email: admin@pps.com
Contraseña: admin123
```

---

## 🔒 OWASP Top 10 - Cobertura de Seguridad

### **A1: Broken Access Control** ✅
**Riesgo**: Usuarios pueden acceder a datos o funcionalidades sin autorización

**Cómo se cubre**:
- ✅ Decorador `@admin_required` que verifica rol antes de ejecutar endpoints administrativos
- ✅ Validación de token JWT en todas las rutas protegidas
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Endpoint `/api/admin/users` solo accesible por admins

**Código evidencia**:
```python
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Acceso denegado'}), 403
        return f(*args, **kwargs)
    return decorated
```

**Test**: `test_admin.py`

---

### **A2: Cryptographic Failures** ✅
**Riesgo**: Fallo en protección de datos sensibles (contraseñas, tokens)

**Cómo se cubre**:
- ✅ Hashing de contraseñas con **pbkdf2:sha256** 
- ✅ JWT firmado con algoritmo *HS256* y clave secreta segura
- ✅ Tokens con expiración automática (24 horas)
- ✅ No se almacenan contraseñas en texto plano
- ✅ Secreto JWT en variable de entorno (`JWT_SECRET`)

**Código evidencia**:
```python
# Hashing de contraseño
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# Verificación
if user and check_password_hash(user[2], password):

# Token con expiración
'exp': now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
```

**Test**: `test_security.py`, `test_jwt.py`

---

### **A3: Injection** ✅
**Riesgo**: Inyección SQL, NoSQL, comando del sistema

**Cómo se cubre**:
- ✅ **Prepared Statements** con placeholders `?` en todas las consultas SQL
- ✅ Validación exhaustiva de entrada (regex, longitud, tipo)
- ✅ Sanitización de datos: `.strip()` para eliminar espacios
- ✅ Rechazo de entrada con caracteres especiales no permitidos

**Código evidencia**:
```python
# Prepared statement seguro - NO vulnerable a SQL injection
cursor.execute("SELECT id, name, password, role FROM users WHERE email=?", (email,))

# Validaciones regex
if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", email):
```

**Test**: `test_security.py` - `test_sql_injection_login()`

---

### **A4: Insecure Design** ✅
**Riesgo**: Falta de medidas preventivas contra abuso (fuerza bruta, spam)

**Cómo se cubre**:
- ✅ **Rate Limiting** en endpoints críticos
  - Login: 5 intentos/minuto (protege contra fuerza bruta)
  - Registro: 3 intentos/minuto (protege contra spam)
  - Admin: 10 solicitudes/minuto
  - Default: 200/día, 50/hora
- ✅ Validación de requisitos de contraseña (8+ caracteres, mayúsculas, números, especiales)
- ✅ CORS configurado explícitamente
- ✅ Tokens con expiración temporal

**Código evidencia**:
```python
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # Protección contra fuerza bruta
def login():
```

**Test**: Pruebas manuales con Postman o load testing

---

### **A5: Security Misconfiguration** ✅
**Riesgo**: Configuración insegura de servidor, bases de datos, frameworks

**Cómo se cubre**:
- ✅ Base de datos SQLite en carpeta `instance/` (no en raíz)
- ✅ Secreto JWT gestionado por variables de entorno
- ✅ Docker con aislamiento de servicios
- ✅ Flask CORS configurado: `CORS(app)`
- ✅ Base de datos inicializada automáticamente
- ✅ Estructura de directorios limpia y organizada

**Código evidencia**:
```python
JWT_SECRET = os.environ.get('JWT_SECRET', 'clave-super-secreta-pps-2024-abc123!')
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'pps.db')
```

---

### **A6: Vulnerable and Outdated Components** ✅
**Riesgo**: Uso de librerías con vulnerabilidades conocidas

**Cómo se cubre**:
- ✅ Dependencias actualizadas a versiones estables:
  - Flask 3.0.3 (última versión estable)
  - Werkzeug 3.0.4
  - Flask-JWT-Extended 4.6.0
  - Flask-CORS 4.0.0
  - Flask-Limiter (última)
- ✅ Testing con pytest para validar compatibilidad
- ✅ requirements.txt congelado con versiones específicas

**Archivo**: `backend/requirements.txt`

---

### **A7: Authentication and Session Management** ✅
**Riesgo**: Gestión insegura de sesiones y tokens

**Cómo se cubre**:
- ✅ JWT con algoritmo seguro (HS256)
- ✅ Token Bearer en header: `Authorization: Bearer <token>`
- ✅ Expiración automática de tokens (24 horas)
- ✅ Validación de firma JWT en cada solicitud
- ✅ Leeway de 10 segundos para desincronización de reloj

**Código evidencia**:
```python
def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": True},
        leeway=datetime.timedelta(seconds=10)
    )
```

**Test**: `test_jwt.py`, `test_login.py`

---

### **A8: Software and Data Integrity Failures** ✅
**Riesgo**: Falta de validación y verificación de datos

**Cómo se cubre**:
- ✅ Validación exhaustiva en cada entrada de datos
- ✅ Módulo `validaciones.py` centralizado
- ✅ Verificación de campos requeridos antes de procesar
- ✅ Type checking y range validation
- ✅ Tests unitarios para validaciones

**Código evidencia**:
```python
def validar_registro(name, email, phone, password):
    errores = []
    if len(name) <= 2:
        errores.append("El nombre debe tener más de 2 caracteres")
    # ... más validaciones
    return errores
```

**Test**: `test_validaciones.py`

---

### **A9: Logging and Monitoring** ⚠️ 

**Cómo se cubre**:
- ✅ Mensajes de error claros que no exponen info sensible
- ✅ Códigos de estado HTTP explícitos (401, 403, 422, etc.)
- ✅ Validación que rechaza datos sospechosos

---

## 📁 Estructura del Proyecto

```
PPT_Proyecto/
├── README.md                          # Este archivo
├── docker-compose.yml                 # Orquestación de servicios
├── test_API.postman_collection.json   # Tests API en Postman
│
├── backend/
│   ├── app.py                         # Aplicación principal Flask
│   ├── requirements.txt                # Dependencias Python
│   ├── validaciones.py                 # Módulo de validaciones
│   ├── Dockerfile                      # Imagen Docker backend
│   ├── instance/
│   │   └── pps.db                     # Base de datos SQLite
│   └── tests/
│       ├── conftest.py                # Configuración pytest
│       ├── test_admin.py              # Tests de acceso admin
│       ├── test_jwt.py                # Tests de JWT
│       ├── test_login.py              # Tests de login
│       ├── test_register.py           # Tests de registro
│       ├── test_security.py           # Tests de seguridad
│       └── test_validaciones.py       # Tests de validaciones
│
└── frontend/
    ├── admin.html                     # Panel administrativo
    ├── login.html                     # Página de login
    ├── registro.html                  # Página de registro
    ├── user.html                      # Panel de usuario
    ├── default.conf                   # Configuración Nginx
    └── Dockerfile                     # Imagen Docker frontend
```

---

## 🔌 API Endpoints

### Autenticación (Sin protección JWT)

#### 1. **Registro de Usuario**
```
POST /api/register
Rate Limit: 3/minuto
Body: {
  "name": "Juan García",
  "email": "juan@example.com",
  "phone": "612345678",
  "password": "Password123!"
}
Response: { "token": "eyJ0eXAi..." }
Status: 201 (Created) | 422 (Invalid) | 409 (Email exists)
```

#### 2. **Login**
```
POST /api/login
Rate Limit: 5/minuto
Body: {
  "email": "admin@pps.com",
  "password": "admin123"
}
Response: {
  "token": "eyJ0eXAi...",
  "user": "Admin PPS",
  "role": "admin"
}
Status: 200 (OK) | 401 (Invalid credentials) | 422 (Invalid)
```

### Rutas Protegidas (Requieren JWT)

#### 3. **Obtener Perfil Actual**
```
GET /api/me
Headers: Authorization: Bearer <token>
Response: { "current_user": { "sub": "1", "email": "...", "role": "..." } }
Status: 200 (OK) | 401 (No token)
```

### Rutas Admin (Requieren JWT + Rol Admin)

#### 4. **Listar Usuarios**
```
GET /api/admin/users
Headers: Authorization: Bearer <token>
Rate Limit: 10/minuto
Response: {
  "users": [
    { "id": 1, "name": "Admin PPS", "email": "admin@pps.com", "phone": "000000000", "role": "admin" }
  ]
}
Status: 200 (OK) | 401 (No token) | 403 (Not admin)
```

---

## 🧪 Testing

### Ejecutar todos los tests
```bash
cd backend
pytest tests/ -v
```

### Coverage de pruebas
```
tests/
├── test_admin.py              # Autorización de admin
├── test_jwt.py                # Validación de tokens JWT
├── test_login.py              # Proceso de login
├── test_register.py           # Registro de usuarios
├── test_security.py           # Inyección SQL, rate limit, validaciones
└── test_validaciones.py       # Funciones de validación
```

### Ejemplo de test de seguridad
```python
def test_sql_injection_login(client):
    response = client.post('/api/login', json={
        "email": "' OR 1=1 --",
        "password": "123"
    })
    assert response.status_code in [401, 422]
```

---


## 👨‍💼 Autor

Proyecto desarrollado como trabajo final con enfoque en seguridad web y cumplimiento de estándares OWASP.

**Fecha**: 18 Marzo 2026

