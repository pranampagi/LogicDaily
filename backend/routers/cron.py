import os
import random
import datetime
import logging
from fastapi import APIRouter, Header, HTTPException, status, BackgroundTasks, Depends
from database import SessionLocal
from cache import get_cache
from config import settings
import models
import schemas

logger = logging.getLogger("LogicDailyCron")

router = APIRouter(
    prefix="/api/cron",
    tags=["Cron Jobs"]
)

def rotate_daily_challenge(cache_client):
    """
    Selects a new active daily challenge, marks the old one inactive, 
    and flushes/updates the cache. Runs asynchronously in a background worker.
    """
    logger.info("Starting daily challenge rotation background task...")
    db = SessionLocal()
    try:
        # 1. Fetch current active question
        current_active = db.query(models.Question).filter(models.Question.is_active == True).first()

        # 2. Query for candidate questions (excluding current active one to guarantee a change)
        query = db.query(models.Question)
        if current_active:
            query = query.filter(models.Question.id != current_active.id)
        
        candidates = query.all()
        
        if not candidates:
            # If no alternative questions exist
            if current_active:
                logger.info("No alternative candidates found. Keeping current challenge active.")
                return
            else:
                logger.warning("No questions found in database to rotate.")
                return
        
        # 3. Pick a random candidate
        next_active = random.choice(candidates)

        # 4. Perform DB updates in transaction
        if current_active:
            current_active.is_active = False
            # We don't delete, we just toggle is_active = False
        
        next_active.is_active = True
        next_active.activated_at = datetime.datetime.now(datetime.UTC)
        db.commit()
        db.refresh(next_active)
        logger.info(f"Successfully rotated daily question to ID {next_active.id}: '{next_active.title}'")

        # 5. Invalidate old cache and pre-warm with the new challenge
        cache_client.delete("daily_question")
        q_response = schemas.QuestionResponse.model_validate(next_active)
        cache_client.set("daily_question", q_response.model_dump_json(), expire_seconds=86400)
        logger.info("Daily question cache successfully pre-warmed.")

    except Exception as e:
        logger.error(f"Error during daily challenge rotation: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/rotate")
def trigger_rotation(
    background_tasks: BackgroundTasks, 
    authorization: str = Header(default=None),
    cache_client = Depends(get_cache)
):
    """
    Trigger daily question rotation.
    Protected by checking the Authorization Bearer token header.
    Matches the CRON_KEY environment variable.
    """
    cron_key = settings.CRON_KEY
    expected_auth = f"Bearer {cron_key}"

    if not authorization or authorization != expected_auth:
        logger.warning("Unauthorized attempt to access Cron rotation endpoint.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing Cron token."
        )

    logger.info("Cron key verification successful. Queuing rotation task.")
    background_tasks.add_task(rotate_daily_challenge, cache_client)
    
    return {
        "status": "success",
        "message": "Daily challenge rotation triggered in background."
    }
