from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from cache import get_cache
import models
import schemas
import json
import logging

logger = logging.getLogger("LogicDailyAPI")

router = APIRouter(
    prefix="/api/submissions",
    tags=["Submissions"]
)

@router.post("", response_model=schemas.SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    submission: schemas.SubmissionCreate,
    x_user_id: int = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
    cache_client = Depends(get_cache)
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

    # Invalidate leaderboard cache
    try:
        cache_client.delete("leaderboard")
        logger.info("Leaderboard cache invalidated due to new submission")
    except Exception as e:
        logger.warning(f"Failed to invalidate leaderboard cache: {e}")

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

@router.get("/leaderboard")
def get_leaderboard(
    response: Response,
    db: Session = Depends(get_db),
    cache_client = Depends(get_cache)
):
    """
    Get the global leaderboard ranking users by correct submissions and accuracy.
    Cached for 1 hour.
    """
    # 0. Check if physical SQLite database file exists on disk (if using SQLite)
    from database import DATABASE_URL
    import os
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            try:
                cache_client.delete("leaderboard")
            except Exception as e:
                logger.warning(f"Failed to clear empty leaderboard cache: {e}")
            return []

    # 0.5. Check if database has any submissions at all
    try:
        if db.query(models.Submission).count() == 0:
            # If database is empty, invalidate cache and return empty leaderboard
            try:
                cache_client.delete("leaderboard")
            except Exception as e:
                logger.warning(f"Failed to clear empty leaderboard cache: {e}")
            return []
    except SQLAlchemyError as e:
        logger.warning(f"Database query failed, tables might be missing: {e}. Re-creating tables dynamically...")
        try:
            from database import Base, engine
            Base.metadata.create_all(bind=engine)
            cache_client.delete("leaderboard")
        except Exception as ce:
            logger.error(f"Failed to dynamically re-create database tables: {ce}")
        return []

    # 1. Try cache
    cached_data = cache_client.get("leaderboard")
    if cached_data:
        try:
            logger.info("Serving leaderboard from cache")
            response.headers["X-Cache"] = "HIT"
            return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to parse cached leaderboard: {e}")
            
    response.headers["X-Cache"] = "MISS"
    logger.info("Leaderboard cache miss. Calculating from database...")
    
    # 2. Query stats
    results = db.query(
        models.User.username,
        func.count(models.Submission.id).label("total_submissions"),
        func.sum(case((models.Submission.is_correct == True, 1), else_=0)).label("correct_submissions")
    ).join(
        models.Submission, models.User.id == models.Submission.user_id
    ).group_by(
        models.User.id, models.User.username
    ).all()
    
    leaderboard_data = []
    for username, total, correct in results:
        score = correct
        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        leaderboard_data.append({
            "username": username,
            "score": score,
            "accuracy": accuracy
        })
        
    # Sort: score desc, accuracy desc, username asc
    leaderboard_data.sort(key=lambda x: (-x["score"], -x["accuracy"], x["username"]))
    
    # 3. Cache results for 1 hour (3600 seconds)
    try:
        cache_client.set("leaderboard", json.dumps(leaderboard_data), expire_seconds=3600)
    except Exception as e:
        logger.warning(f"Failed to cache leaderboard: {e}")
        
    return leaderboard_data
