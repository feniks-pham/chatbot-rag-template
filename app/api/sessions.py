from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db, Session as SessionModel
from app.models.schemas import SessionResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session(db: Session = Depends(get_db)):
    """Create a new chat session"""
    logger.info("Creating new chat session")
    try:
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

@router.get("/session/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session information"""
    logger.info(f"Getting session info for: {session_id}")
    try:
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
