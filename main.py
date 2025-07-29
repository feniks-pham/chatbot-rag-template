from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import sessions, chat, tts
from app.models.database import create_tables
from app.services.crawler import crawl_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):  # Use underscore to indicate unused parameter
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        logger.info("Starting application initialization...")
        
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Initialize chat service
        from app.core.chat_service import chat_service
        chat_service.initialize_vector_store()
        logger.info("Vector store initialized successfully")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Starting application shutdown...")
        await crawl_service.close()
        logger.info("Crawler service closed successfully")
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)

app = FastAPI(
    title="Trung Nguyen Legend Cafe Chatbot",
    description="RAG chatbot for Trung Nguyen Legend Cafe",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(tts.router, prefix="/api/v1", tags=["tts"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Trung Nguyen Legend Cafe Chatbot API"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}
