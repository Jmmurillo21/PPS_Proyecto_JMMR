def test_sql_injection_login(client):

    response = client.post('/api/login', json={
        "email": "' OR 1=1 --",
        "password": "123"
    })

    assert response.status_code in [401,422]


def test_empty_body(client):

    response = client.post('/api/login', json={})

    assert response.status_code in [400,422]


def test_long_input_register(client):

    response = client.post('/api/register', json={
        "name": "A"*500,
        "email": "long@test.com",
        "phone": "612345678",
        "password": "Password123!"
    })

    assert response.status_code in [201,422]