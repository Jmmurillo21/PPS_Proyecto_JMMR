def test_me_requires_token(client):

    response = client.get('/api/me')

    assert response.status_code == 401


def test_me_with_token(client):

    r = client.post('/api/register', json={
        "name": "Luis",
        "email": "luis@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    data = r.get_json()

    assert "token" in data

    token = data["token"]

    response = client.get(
        '/api/me',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_me_invalid_token(client):

    response = client.get(
        '/api/me',
        headers={"Authorization": "Bearer token_invalido"}
    )

    assert response.status_code == 401