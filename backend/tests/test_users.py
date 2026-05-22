def test_register_user(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_username(client):
    payload1 = {
        "username": "dupuser",
        "email": "user1@example.com",
        "password": "password"
    }
    payload2 = {
        "username": "dupuser",
        "email": "user2@example.com",
        "password": "password"
    }
    client.post("/api/users/register", json=payload1)
    response = client.post("/api/users/register", json=payload2)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_register_duplicate_email(client):
    payload1 = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "password"
    }
    payload2 = {
        "username": "user2",
        "email": "dup@example.com",
        "password": "password"
    }
    client.post("/api/users/register", json=payload1)
    response = client.post("/api/users/register", json=payload2)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client):
    register_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "correct_password"
    }
    client.post("/api/users/register", json=register_payload)

    login_payload = {
        "email": "login@example.com",
        "password": "correct_password"
    }
    response = client.post("/api/users/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "loginuser"
    assert "id" in data

def test_login_invalid_password(client):
    register_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "correct_password"
    }
    client.post("/api/users/register", json=register_payload)

    login_payload = {
        "email": "login@example.com",
        "password": "wrong_password"
    }
    response = client.post("/api/users/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_nonexistent_email(client):
    login_payload = {
        "email": "missing@example.com",
        "password": "any_password"
    }
    response = client.post("/api/users/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]
