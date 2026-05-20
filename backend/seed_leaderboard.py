import os
import sys
import json
import hashlib

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed():
    # Make sure tables exist
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Clean up existing seeded users and submissions to allow repeat runs
        usernames = ["alex", "bob", "suarez", "guest_thinker"]
        users_to_delete = db.query(models.User).filter(models.User.username.in_(usernames)).all()
        user_ids = [u.id for u in users_to_delete]
        
        if user_ids:
            # Delete submissions of these users
            db.query(models.Submission).filter(models.Submission.user_id.in_(user_ids)).delete(synchronize_session=False)
            # Delete users
            db.query(models.User).filter(models.User.username.in_(usernames)).delete(synchronize_session=False)
            db.commit()
            
        # Clean up specific seed questions if they exist to keep it clean
        question_titles = [
            "Math Basics",
            "Vocabulary Antonym",
            "Syllogism Logic",
            "Geometric Progression",
            "Basic Geometry"
        ]
        db.query(models.Question).filter(models.Question.title.in_(question_titles)).delete(synchronize_session=False)
        db.commit()

        # 2. Add Users
        users = {}
        user_data = [
            ("alex", "alex@example.com"),
            ("bob", "bob@example.com"),
            ("suarez", "suarez@example.com"),
            ("guest_thinker", "guest@example.com")
        ]
        for username, email in user_data:
            user = models.User(
                username=username,
                email=email,
                hashed_password=hash_password("password")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users[username] = user
            print(f"Created user: {username}")

        # 3. Add Questions
        questions = []
        questions_data = [
            {
                "title": "Math Basics",
                "category": "mathematics",
                "content": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4"
            },
            {
                "title": "Vocabulary Antonym",
                "category": "verbal",
                "content": "Which word is an antonym of fast?",
                "options": ["slow", "quick", "speedy", "rapid"],
                "correct_answer": "slow"
            },
            {
                "title": "Syllogism Logic",
                "category": "logical",
                "content": "If all A are B, and all B are C, are all A C?",
                "options": ["Yes", "No"],
                "correct_answer": "Yes"
            },
            {
                "title": "Geometric Progression",
                "category": "mathematics",
                "content": "Next number in the sequence: 2, 4, 8, 16, ...",
                "options": ["20", "24", "32", "36"],
                "correct_answer": "32"
            },
            {
                "title": "Basic Geometry",
                "category": "logical",
                "content": "Which shape has 3 sides?",
                "options": ["Square", "Circle", "Triangle", "Rectangle"],
                "correct_answer": "Triangle"
            }
        ]

        for q in questions_data:
            question = models.Question(
                title=q["title"],
                category=q["category"],
                content=q["content"],
                options=json.dumps(q["options"]),
                correct_answer=q["correct_answer"],
                is_active=False
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            questions.append(question)
            print(f"Created question: {q['title']}")

        # 4. Add Submissions
        # alex: 5 correct / 5 submissions (100% accuracy)
        for q in questions:
            sub = models.Submission(
                user_id=users["alex"].id,
                question_id=q.id,
                submitted_answer=q.correct_answer,
                is_correct=True
            )
            db.add(sub)

        # bob: 3 correct / 5 submissions (60% accuracy)
        db.add(models.Submission(user_id=users["bob"].id, question_id=questions[0].id, submitted_answer=questions[0].correct_answer, is_correct=True))
        db.add(models.Submission(user_id=users["bob"].id, question_id=questions[1].id, submitted_answer=questions[1].correct_answer, is_correct=True))
        db.add(models.Submission(user_id=users["bob"].id, question_id=questions[2].id, submitted_answer="No", is_correct=False))
        db.add(models.Submission(user_id=users["bob"].id, question_id=questions[3].id, submitted_answer=questions[3].correct_answer, is_correct=True))
        db.add(models.Submission(user_id=users["bob"].id, question_id=questions[4].id, submitted_answer="Square", is_correct=False))

        # suarez: 2 correct / 2 submissions (100% accuracy)
        db.add(models.Submission(user_id=users["suarez"].id, question_id=questions[0].id, submitted_answer=questions[0].correct_answer, is_correct=True))
        db.add(models.Submission(user_id=users["suarez"].id, question_id=questions[1].id, submitted_answer=questions[1].correct_answer, is_correct=True))

        # guest_thinker: 1 correct / 2 submissions (50% accuracy)
        db.add(models.Submission(user_id=users["guest_thinker"].id, question_id=questions[0].id, submitted_answer=questions[0].correct_answer, is_correct=True))
        db.add(models.Submission(user_id=users["guest_thinker"].id, question_id=questions[1].id, submitted_answer="quick", is_correct=False))

        db.commit()
        print("Successfully seeded database with leaderboard dummy data!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
