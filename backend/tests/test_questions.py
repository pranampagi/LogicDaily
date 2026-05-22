def test_create_question(client):
    payload = {
        "category": "logical",
        "title": "Syllogism Test",
        "content": "All A are B. All B are C. Is A C?",
        "options": ["Yes", "No", "Maybe"],
        "correct_answer": "Yes"
    }
    response = client.post("/api/questions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Syllogism Test"
    assert data["category"] == "logical"
    assert "id" in data
    assert not data["is_active"]

def test_create_duplicate_question_title(client):
    payload = {
        "category": "logical",
        "title": "Unique Title",
        "content": "Is this unique?",
        "options": ["Yes", "No"],
        "correct_answer": "Yes"
    }
    response1 = client.post("/api/questions", json=payload)
    assert response1.status_code == 201

    # Try creating again with same title
    response2 = client.post("/api/questions", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_read_questions(client):
    payload1 = {
        "category": "logical",
        "title": "Title 1",
        "content": "Content 1",
        "options": ["A", "B"],
        "correct_answer": "A"
    }
    payload2 = {
        "category": "mathematics",
        "title": "Title 2",
        "content": "Content 2",
        "options": ["C", "D"],
        "correct_answer": "D"
    }
    client.post("/api/questions", json=payload1)
    client.post("/api/questions", json=payload2)

    response = client.get("/api/questions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {q["title"] for q in data} == {"Title 1", "Title 2"}

def test_read_single_question(client):
    payload = {
        "category": "verbal",
        "title": "Verbal Test",
        "content": "Antonym of hot?",
        "options": ["Cold", "Warm"],
        "correct_answer": "Cold"
    }
    create_resp = client.post("/api/questions", json=payload).json()
    question_id = create_resp["id"]

    response = client.get(f"/api/questions/{question_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Verbal Test"

def test_read_nonexistent_question(client):
    response = client.get("/api/questions/9999")
    assert response.status_code == 404

def test_update_question(client):
    payload = {
        "category": "verbal",
        "title": "Verbal Test",
        "content": "Antonym of hot?",
        "options": ["Cold", "Warm"],
        "correct_answer": "Cold"
    }
    create_resp = client.post("/api/questions", json=payload).json()
    question_id = create_resp["id"]

    update_payload = {
        "title": "Verbal Test Updated",
        "correct_answer": "Cold"
    }
    response = client.put(f"/api/questions/{question_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Verbal Test Updated"
    assert response.json()["category"] == "verbal"  # Unchanged

def test_delete_question(client):
    payload = {
        "category": "verbal",
        "title": "Delete Me",
        "content": "Delete test",
        "options": ["Yes"],
        "correct_answer": "Yes"
    }
    create_resp = client.post("/api/questions", json=payload).json()
    question_id = create_resp["id"]

    # Delete question
    del_response = client.delete(f"/api/questions/{question_id}")
    assert del_response.status_code == 204

    # Verify 404 on GET
    get_response = client.get(f"/api/questions/{question_id}")
    assert get_response.status_code == 404
