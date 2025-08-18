from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from opensearchpy import OpenSearch
from datetime import datetime, timezone

from app.models.database import get_db, Session as SessionModel
from app.models.opensearch import get_opensearch_db
from app.models.schemas import SessionResponse
from app.utils.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)
router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    logger.info("Creating new chat session")
    if settings.is_postgres:
        try:
            db = next(get_db())
            session_id = uuid4()
            session = SessionModel(id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)
            
            logger.info(f"New session created successfully: {session_id}")
            return SessionResponse(
                id=session.id,
                created_at=session.created_at
            )
        except Exception as e:
            logger.error(f"Error creating session: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    
    else:
        try:
            client = next(get_opensearch_db())
            session_id = uuid4()
            now = datetime.now().strftime("%Y%m%d")
            body = {
                "id": session_id,
                "created_at": now,
                "updated_at": now
            }
            client.index(index="sessions", body=body)
            logger.info(f"New session created successfully: {session_id}")
            return SessionResponse(
                id=session_id,
                created_at=now
            )
        except Exception as e:
            logger.error(f"Error creating session: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    logger.info(f"Getting session info for: {session_id}")
    if settings.is_postgres:
        try:
            db = next(get_db())
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                logger.warning(f"Session not found: {session_id}")
                raise HTTPException(status_code=404, detail="Session not found")
            
            logger.info(f"Session found: {session_id}")
            return SessionResponse(
                id=session.id,
                created_at=session.created_at
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")
    
    else:
        try:
            client = next(get_opensearch_db())
            response = client.search(
                index="sessions",
                body={
                    "query": {
                        "term": {  # sử dụng term nếu session_id là keyword
                            "id": session_id
                           }
                    },
                    "size": 1
                }
            )

            if response["hits"]["total"]["value"] <= 0:
                logger.warning(f"Session not found: {session_id}")
                raise HTTPException(status_code=404, detail="Session not found")
            
            res = client.get(index="sessions", id=session_id)
            created_at = res["_source"]["created_at"]
            
            logger.info(f"Session found: {session_id}")
            return SessionResponse(
                id=session_id,
                created_at=created_at
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")