import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        init_db()
        yield client