from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.database import get_db, Session as SessionModel
from app.models.schemas import ChatRequest, ChatResponse
from app.core.chat_service import chat_service
from app.core.intent_router import IntentRouter, QueryRewriter
from app.services.llm import LLMService
from app.utils.logger import get_logger
import json

logger = get_logger(__name__)
router = APIRouter()

# Initialize services
llm_service = LLMService()
intent_router = IntentRouter(llm_service)
query_rewriter = QueryRewriter(llm_service)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint"""
    logger.info(f"Chat request received - session_id: {request.session_id}, query: {request.query[:50]}...")
    try:
        # Check if session exists
        session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        if not session:
            logger.warning(f"Session not found: {request.session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Session found: {request.session_id}")
        
        # Initialize vector store if not already done
        chat_service.initialize_vector_store()
        logger.info("Vector store initialization completed")
        
        # Get chat history
        history = chat_service.get_chat_history(db, str(request.session_id))
        logger.info(f"Retrieved {len(history)} messages from chat history")
        
        # Rewrite query based on history
        rewritten_query = await query_rewriter.rewrite_query(request.query, history)
        logger.info(f"Query rewritten: '{request.query}' -> '{rewritten_query}'")
        
        # Classify intent
        intent = await intent_router.classify_intent(rewritten_query)
        logger.info(f"Intent classified as: {intent}")
        
        # Generate response
        logger.info("Starting response generation...")
        response = await chat_service.response_generator.generate_response(
            rewritten_query, intent, history
        )
        logger.info(f"Response generated successfully, length: {len(response)}")
        
        # Save user message
        chat_service.save_message(
            db, str(request.session_id), "user", request.query, intent
        )
        logger.info("User message saved to history")
        
        # Save assistant response
        chat_service.save_message(
            db, str(request.session_id), "assistant", response, intent
        )
        logger.info("Assistant response saved to history")
        
        logger.info(f"Chat request completed successfully for session: {request.session_id}")
        return ChatResponse(
            response=response,
            intent=intent,
            session_id=request.session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint with streaming response"""
    logger.info(f"Streaming chat request received - session_id: {request.session_id}, query: {request.query[:50]}...")
    
    async def generate_stream():
        try:
            # Check if session exists
            session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
            if not session:
                logger.warning(f"Session not found: {request.session_id}")
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                return
            
            logger.info(f"Session found: {request.session_id}")
            
            # Initialize vector store if not already done
            chat_service.initialize_vector_store()
            logger.info("Vector store initialization completed")
            
            # Get chat history
            history = chat_service.get_chat_history(db, str(request.session_id))
            logger.info(f"Retrieved {len(history)} messages from chat history")
            
            # Rewrite query based on history
            rewritten_query = await query_rewriter.rewrite_query(request.query, history)
            logger.info(f"Query rewritten: '{request.query}' -> '{rewritten_query}'")
            
            # Classify intent
            intent = await intent_router.classify_intent(rewritten_query)
            logger.info(f"Intent classified as: {intent}")
            
            # Send intent information
            yield f"data: {json.dumps({'type': 'intent', 'intent': intent})}\n\n"
            
            # Generate streaming response
            logger.info("Starting streaming response generation...")
            stream_generator = chat_service.response_generator.generate_streaming_response(
                rewritten_query, intent, history
            )
            
            full_response = ""
            async for chunk in stream_generator:
                full_response += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            logger.info(f"Streaming response completed, total length: {len(full_response)}")
            
            # Save user message
            chat_service.save_message(
                db, str(request.session_id), "user", request.query, intent
            )
            logger.info("User message saved to history")
            
            # Save assistant response
            chat_service.save_message(
                db, str(request.session_id), "assistant", full_response, intent
            )
            logger.info("Assistant response saved to history")
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'session_id': str(request.session_id)})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming chat error for session {request.session_id}: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    try:
        # Check if session exists
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = chat_service.get_chat_history(db, session_id)
        return {"session_id": session_id, "history": history}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")
