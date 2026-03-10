import re

def validar_registro(name, email, phone, password):
    errores = []

    # ── NAME ──────────────────────────────────────────
    if len(name) <= 2:
        errores.append("El nombre debe tener más de 2 caracteres")
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", name):
        errores.append("El nombre solo puede contener letras y espacios")

    # ── TELÉFONO ESPAÑOL ──────────────────────────────
    if not re.match(r"^[6789]\d{8}$", phone):
        errores.append("El teléfono debe tener 9 dígitos y empezar por 6, 7, 8 o 9")

    # ── EMAIL ─────────────────────────────────────────
    patron_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    if not re.match(patron_email, email):
        errores.append("El email no tiene un formato válido")

    # ── PASSWORD ──────────────────────────────────────
    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
        errores.append("La contraseña debe tener al menos una mayúscula")
    if not re.search(r"[a-z]", password):
        errores.append("La contraseña debe tener al menos una minúscula")
    if not re.search(r"[0-9]", password):
        errores.append("La contraseña debe tener al menos un número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errores.append("La contraseña debe tener al menos un carácter especial (!@#$...)")

    return errores


def validar_login(email, password):
    errores = []

    if not email:
        errores.append("El email es requerido")
    if not password:
        errores.append("La contraseña es requerida")

    return errores