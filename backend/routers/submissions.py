from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/api/submissions",
    tags=["Submissions"]
)

@router.post("", response_model=schemas.SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    submission: schemas.SubmissionCreate,
    x_user_id: int = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
):
    # 1. Verify User exists
    user = db.query(models.User).filter(models.User.id == x_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    # 2. Verify Question exists
    question = db.query(models.Question).filter(models.Question.id == submission.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Question not found"
        )

    # 3. Check if user already submitted an answer for this question
    existing_sub = db.query(models.Submission).filter(
        models.Submission.user_id == x_user_id,
        models.Submission.question_id == submission.question_id
    ).first()
    
    if existing_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You have already submitted an answer for today's challenge."
        )

    # 4. Check if answer is correct
    is_correct = (submission.submitted_answer == question.correct_answer)

    # 5. Save submission
    db_submission = models.Submission(
        user_id=x_user_id,
        question_id=submission.question_id,
        submitted_answer=submission.submitted_answer,
        is_correct=is_correct
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

@router.get("/status/{question_id}")
def get_submission_status(
    question_id: int,
    x_user_id: int = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
):
    sub = db.query(models.Submission).filter(
        models.Submission.user_id == x_user_id,
        models.Submission.question_id == question_id
    ).first()
    
    if sub:
        return {
            "has_submitted": True,
            "selected_answer": sub.submitted_answer,
            "is_correct": sub.is_correct
        }
    return {
        "has_submitted": False,
        "selected_answer": None,
        "is_correct": False
    }
