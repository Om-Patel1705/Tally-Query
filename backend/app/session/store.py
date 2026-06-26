import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)

SESSION_STORE: Dict[str, Dict[str, Any]] = {}
SESSION_TTL_MINUTES = 30


def start_cleanup_task():
    asyncio.create_task(_cleanup_loop())


async def _cleanup_loop():
    while True:
        await asyncio.sleep(300)  # every 5 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=SESSION_TTL_MINUTES)
        expired = [k for k, v in SESSION_STORE.items() if v["created_at"] < cutoff]
        for k in expired:
            logger.info(f"Cleaning up expired session: {k}")
            del SESSION_STORE[k]


def save_session(session_id: str, df: pd.DataFrame, file_name: str, metadata: Dict[str, Any]):
    """Create a new session with empty query history."""
    SESSION_STORE[session_id] = {
        "df": df,
        "file_name": file_name,
        "metadata": metadata,
        "created_at": datetime.utcnow(),
        "query_history": [],  # Store executed queries
    }
    logger.info(f"Session created: {session_id}")


def get_session(session_id: str) -> Dict[str, Any] | None:
    return SESSION_STORE.get(session_id)


def delete_session(session_id: str) -> bool:
    if session_id in SESSION_STORE:
        logger.info(f"Deleting session: {session_id}")
        del SESSION_STORE[session_id]
        return True
    return False


def add_query_to_history(session_id: str, query: str) -> None:
    """Add an executed query to the session history."""
    session = SESSION_STORE.get(session_id)
    if session:
        # Keep only last 5 queries
        if len(session["query_history"]) >= 5:
            session["query_history"].pop(0)
        
        session["query_history"].append({
            "query": query,
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.info(f"Query added to history for session {session_id}. Total queries: {len(session['query_history'])}")


def get_query_history(session_id: str) -> List[str]:
    """Get the last N executed queries for a session."""
    session = SESSION_STORE.get(session_id)
    if session and session["query_history"]:
        return [q["query"] for q in session["query_history"]]
    return []

