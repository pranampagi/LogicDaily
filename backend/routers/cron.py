import os
import logging
from fastapi import APIRouter, Header, HTTPException, status

logger = logging.getLogger("LogicDailyCron")

router = APIRouter(
    prefix="/api/cron",
    tags=["Cron Jobs"]
)

@router.post("/rotate")
def trigger_rotation(authorization: str = Header(default=None)):
    """
    Trigger daily question rotation.
    Protected by checking the Authorization Bearer token header.
    Matches the CRON_KEY environment variable.
    """
    cron_key = os.getenv("CRON_KEY", "dev_cron_key")
    expected_auth = f"Bearer {cron_key}"

    if not authorization or authorization != expected_auth:
        logger.warning("Unauthorized attempt to access Cron rotation endpoint.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing Cron token."
        )

    logger.info("Cron key verification successful.")
    return {
        "status": "authorized",
        "message": "Cron authorization successful. Ready for daily question rotation logic."
    }
