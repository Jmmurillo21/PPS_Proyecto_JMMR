from validaciones import validar_registro, validar_login


def test_validar_registro_ok():

    errores = validar_registro(
        "Juan",
        "juan@test.com",
        "612345678",
        "Password123!"
    )

    assert errores is None or errores == []


def test_validar_registro_email_invalido():

    errores = validar_registro(
        "Juan",
        "correo_invalido",
        "612345678",
        "Password123!"
    )

    assert errores


def test_validar_login_ok():

    errores = validar_login(
        "test@test.com",
        "Password123!"
    )

    assert errores is None or errores == []


def test_validar_login_email_invalido():

    errores = validar_login(
        "",
        ""
    )

    assert errores