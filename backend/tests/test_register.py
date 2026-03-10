def test_register_ok(client):

    response = client.post('/api/register', json={
        "name": "Juan",
        "email": "juan@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    assert response.status_code == 201

    data = response.get_json()

    assert "token" in data
    assert data["message"] == "Registrado OK"


def test_register_missing_fields(client):

    response = client.post('/api/register', json={
        "name": "Juan"
    })

    assert response.status_code == 400


def test_register_duplicate_email(client):

    user = {
        "name": "Pedro",
        "email": "pedro@test.com",
        "phone": "612345678",
        "password": "Password123!"
    }

    client.post('/api/register', json=user)

    response = client.post('/api/register', json=user)

    assert response.status_code in [409,422]


def test_register_invalid_email(client):

    response = client.post('/api/register', json={
        "name": "Juan",
        "email": "correo_invalido",
        "phone": "612345678",
        "password": "Password123!"
    })

    assert response.status_code in [400,422]