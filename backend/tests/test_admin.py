def test_admin_list_users(client):

    login = client.post('/api/login', json={
        "email": "admin@pps.com",
        "password": "admin123"
    })

    token = login.get_json()["token"]

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "users" in data


def test_admin_requires_token(client):

    response = client.get("/api/admin/users")

    assert response.status_code == 401


def test_admin_access_denied(client):

    r = client.post('/api/register', json={
        "name": "Pedro",
        "email": "pedro2@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    data = r.get_json()

    assert "token" in data

    token = data["token"]

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403