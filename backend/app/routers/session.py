from fastapi import APIRouter, HTTPException, Query
import logging
from app.session.store import get_session, delete_session
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status")
async def get_session_status(session_id: str):
    """Check if a session exists and return basic info."""
    logger.info(f"Session status check requested: {session_id}")
    try:
        session = get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Session found: {session_id}")
        return {
            "session_id": session_id,
            "file_name": session["file_name"],
            "row_count": len(session["df"]),
            "created_at": session["created_at"].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking session status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking session status: {str(e)}")


@router.get("/data")
async def get_session_data(session_id: str, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=500)):
    """Get paginated dataset data for preview."""
    logger.info(f"Session data requested: {session_id}, page: {page}, page_size: {page_size}")
    try:
        session = get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        df = session["df"]
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_df = df.iloc[start_idx:end_idx].copy()
        # Replace NaN values with None for JSON compatibility
        page_df = page_df.where(pd.notnull(page_df), None)
        page_data = page_df.to_dict(orient='records')
        
        return {
            "data": page_data,
            "page": page,
            "page_size": page_size,
            "total_rows": total_rows,
            "total_pages": total_pages,
            "columns": df.columns.tolist()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting session data: {str(e)}")


@router.delete("/clear")
async def clear_session(session_id: str):
    """Delete a session from memory."""
    logger.info(f"Session clear requested: {session_id}")
    try:
        success = delete_session(session_id)
        if not success:
            logger.warning(f"Session not found for deletion: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Session cleared successfully: {session_id}")
        return {"message": "Session cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")
