from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "TallyQuery API"
    }