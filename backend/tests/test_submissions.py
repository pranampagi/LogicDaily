def test_submit_answer(client):
    # Register user
    user = client.post("/api/users/register", json={
        "username": "submitter",
        "email": "submitter@example.com",
        "password": "password"
    }).json()

    # Create active question
    question = client.post("/api/questions", json={
        "category": "verbal",
        "title": "Synonym test",
        "content": "Synonym of happy?",
        "options": ["Sad", "Glad"],
        "correct_answer": "Glad"
    }).json()
    # Activate
    client.get("/api/daily")

    # Submit answer
    payload = {
        "question_id": question["id"],
        "submitted_answer": "Glad"
    }
    response = client.post(
        "/api/submissions",
        json=payload,
        headers={"X-User-Id": str(user["id"])}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["is_correct"]
    assert data["submitted_answer"] == "Glad"

def test_submit_answer_twice_fails(client):
    user = client.post("/api/users/register", json={
        "username": "submitter",
        "email": "submitter@example.com",
        "password": "password"
    }).json()

    question = client.post("/api/questions", json={
        "category": "verbal",
        "title": "Synonym test",
        "content": "Synonym of happy?",
        "options": ["Sad", "Glad"],
        "correct_answer": "Glad"
    }).json()
    client.get("/api/daily")

    payload = {
        "question_id": question["id"],
        "submitted_answer": "Glad"
    }
    # Submit first time
    response1 = client.post(
        "/api/submissions",
        json=payload,
        headers={"X-User-Id": str(user["id"])}
    )
    assert response1.status_code == 201

    # Submit second time
    response2 = client.post(
        "/api/submissions",
        json=payload,
        headers={"X-User-Id": str(user["id"])}
    )
    assert response2.status_code == 400
    assert "already submitted" in response2.json()["detail"]

def test_verify_submission_status(client):
    user = client.post("/api/users/register", json={
        "username": "submitter",
        "email": "submitter@example.com",
        "password": "password"
    }).json()

    question = client.post("/api/questions", json={
        "category": "verbal",
        "title": "Synonym test",
        "content": "Synonym of happy?",
        "options": ["Sad", "Glad"],
        "correct_answer": "Glad"
    }).json()
    client.get("/api/daily")

    # Initial check should show has_submitted=False
    chk1 = client.get(
        f"/api/submissions/status/{question['id']}",
        headers={"X-User-Id": str(user["id"])}
    ).json()
    assert not chk1["has_submitted"]

    # Submit
    client.post(
        "/api/submissions",
        json={"question_id": question["id"], "submitted_answer": "Glad"},
        headers={"X-User-Id": str(user["id"])}
    )

    # Second check should show has_submitted=True
    chk2 = client.get(
        f"/api/submissions/status/{question['id']}",
        headers={"X-User-Id": str(user["id"])}
    ).json()
    assert chk2["has_submitted"]
    assert chk2["selected_answer"] == "Glad"
    assert chk2["is_correct"]

def test_leaderboard_rankings(client):
    # Register 3 users
    u1 = client.post("/api/users/register", json={"username": "user1", "email": "u1@ex.com", "password": "password"}).json()
    u2 = client.post("/api/users/register", json={"username": "user2", "email": "u2@ex.com", "password": "password"}).json()
    u3 = client.post("/api/users/register", json={"username": "user3", "email": "u3@ex.com", "password": "password"}).json()

    # Create 2 questions
    q1 = client.post("/api/questions", json={"category": "mathematics", "title": "Question 1", "content": "C1", "options": ["A", "B"], "correct_answer": "A"}).json()
    q2 = client.post("/api/questions", json={"category": "mathematics", "title": "Question 2", "content": "C2", "options": ["A", "B"], "correct_answer": "A"}).json()

    # User 1 submits 2 correct answers (Score: 2, Accuracy: 100%)
    client.post("/api/submissions", json={"question_id": q1["id"], "submitted_answer": "A"}, headers={"X-User-Id": str(u1["id"])})
    client.post("/api/submissions", json={"question_id": q2["id"], "submitted_answer": "A"}, headers={"X-User-Id": str(u1["id"])})

    # User 2 submits 1 correct answer (Score: 1, Accuracy: 100%)
    client.post("/api/submissions", json={"question_id": q1["id"], "submitted_answer": "A"}, headers={"X-User-Id": str(u2["id"])})

    # User 3 submits 1 correct and 1 wrong answer (Score: 1, Accuracy: 50%)
    client.post("/api/submissions", json={"question_id": q1["id"], "submitted_answer": "A"}, headers={"X-User-Id": str(u3["id"])})
    client.post("/api/submissions", json={"question_id": q2["id"], "submitted_answer": "B"}, headers={"X-User-Id": str(u3["id"])})

    # Fetch leaderboard
    leaderboard = client.get("/api/submissions/leaderboard").json()
    
    assert len(leaderboard) == 3
    # Order should be user1 (score 2), user2 (score 1, acc 100%), user3 (score 1, acc 50%)
    assert leaderboard[0]["username"] == "user1"
    assert leaderboard[0]["score"] == 2
    assert leaderboard[0]["accuracy"] == 100.0

    assert leaderboard[1]["username"] == "user2"
    assert leaderboard[1]["score"] == 1
    assert leaderboard[1]["accuracy"] == 100.0

    assert leaderboard[2]["username"] == "user3"
    assert leaderboard[2]["score"] == 1
    assert leaderboard[2]["accuracy"] == 50.0
