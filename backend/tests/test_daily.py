import pytest

def test_get_daily_question_no_questions_404(client):
    response = client.get("/api/daily")
    assert response.status_code == 404

def test_get_daily_question_fallback_to_newest(client):
    # Setup some questions in DB
    client.post("/api/questions", json={
        "category": "verbal",
        "title": "Question 1",
        "content": "First",
        "options": ["A"],
        "correct_answer": "A"
    })
    client.post("/api/questions", json={
        "category": "mathematics",
        "title": "Question 2",
        "content": "Second",
        "options": ["B"],
        "correct_answer": "B"
    })

    # Retrieve daily question: since none are active, should pick newest (Question 2) and activate it
    response = client.get("/api/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Question 2"
    assert data["is_active"]
    assert response.headers.get("X-Cache") == "MISS"

    # Second fetch should trigger Cache HIT
    response_cached = client.get("/api/daily")
    assert response_cached.status_code == 200
    assert response_cached.json()["title"] == "Question 2"
    assert response_cached.headers.get("X-Cache") == "HIT"

def test_cron_rotation_unauthorized(client):
    response = client.post("/api/cron/rotate")
    assert response.status_code == 401

    response_bad_key = client.post(
        "/api/cron/rotate",
        headers={"Authorization": "Bearer wrong_key"}
    )
    assert response_bad_key.status_code == 401

def test_cron_rotation_success(client, db_session):
    # Setup questions
    client.post("/api/questions", json={
        "category": "logical",
        "title": "Question 1",
        "content": "C1",
        "options": ["A"],
        "correct_answer": "A"
    })
    client.post("/api/questions", json={
        "category": "mathematics",
        "title": "Question 2",
        "content": "C2",
        "options": ["B"],
        "correct_answer": "B"
    })

    # Initialize daily question (picks Question 2 as newest active)
    daily_res = client.get("/api/daily").json()
    assert daily_res["title"] == "Question 2"

    # Rotate
    rotate_res = client.post(
        "/api/cron/rotate",
        headers={"Authorization": "Bearer dev_cron_key"}
    )
    assert rotate_res.status_code == 200
    
    # Wait, the rotation task runs in the background. FastAPI BackgroundTasks execute immediately after response is sent in TestClient!
    # Retrieve daily question: should rotate to Question 1
    daily_res_new = client.get("/api/daily").json()
    assert daily_res_new["title"] == "Question 1"
