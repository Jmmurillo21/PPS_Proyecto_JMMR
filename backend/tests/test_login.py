def test_login_ok(client):

    client.post('/api/register', json={
        "name": "Ana",
        "email": "ana@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    response = client.post('/api/login', json={
        "email": "ana@test.com",
        "password": "Password123!"
    })

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data
    assert data["role"] == "user"


def test_login_wrong_password(client):

    client.post('/api/register', json={
        "name": "Carlos",
        "email": "carlos@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    response = client.post('/api/login', json={
        "email": "carlos@test.com",
        "password": "incorrecta"
    })

    assert response.status_code == 401


def test_login_user_not_found(client):

    response = client.post('/api/login', json={
        "email": "fake@test.com",
        "password": "123456"
    })

    assert response.status_code == 401