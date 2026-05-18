import json
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from cache import get_cache
import models
import schemas

logger = logging.getLogger("LogicDailyAPI")

router = APIRouter(
    prefix="/api/daily",
    tags=["Daily Challenge"]
)

@router.get("", response_model=schemas.QuestionResponse)
def get_daily_question(db: Session = Depends(get_db), cache_client = Depends(get_cache)):
    """
    Retrieve the active daily question.
    Checks the Redis/in-memory cache first for high performance.
    Falls back to querying the database, then populates the cache.
    """
    # 1. Try to retrieve from cache
    cached_q = cache_client.get("daily_question")
    if cached_q:
        try:
            logger.info("Serving daily question from cache")
            return json.loads(cached_q)
        except Exception as e:
            logger.warning(f"Failed to parse cached daily question: {e}. Re-querying database.")

    logger.info("Cache miss. Fetching daily question from database")

    # 2. Query the database for the active question
    db_question = db.query(models.Question).filter(models.Question.is_active == True).first()
    
    # 3. Fallback: If no question is set as active, pick the newest question and make it active
    if not db_question:
        logger.info("No active daily question found. Executing newest fallback selection.")
        db_question = db.query(models.Question).order_by(models.Question.created_at.desc()).first()
        
        if not db_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions available in the database. Please create a question first."
            )
        
        # Activate the selected fallback question
        db_question.is_active = True
        db_question.activated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_question)

    # 4. Serialize to Pydantic and populate the cache (cache for 24 hours)
    try:
        q_response = schemas.QuestionResponse.model_validate(db_question)
        cache_client.set("daily_question", q_response.model_dump_json(), expire_seconds=86400)
    except Exception as e:
        logger.warning(f"Failed to write daily question to cache: {e}")

    return db_question
