from typing import List, Dict
import yaml
import os

from langchain.prompts import ChatPromptTemplate
from langchain_postgres import PGVector
from langchain_community.vectorstores import OpenSearchVectorSearch
from sqlalchemy.orm import Session
from opensearchpy import OpenSearch
from datetime import datetime

from app.config.settings import settings
from app.models.database import ChatHistory
from app.services.crawler import crawl_service
from app.services.embeddings import CustomEmbeddings
from app.services.llm import LLMService
from app.utils.logger import get_logger
from app.utils.load_intents import load_intents, load_prompt_template

logger = get_logger(__name__)
    
class ResponseGenerator:
    def __init__(self, llm_service: LLMService, embeddings: CustomEmbeddings, vector_store):
        self.llm_service = llm_service
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.intent = load_intents()
        self.prompts = {}
        
        # Different prompt templates for each intent
        for intent, config in self.intent.items():
            prompt_text = load_prompt_template(config["prompt_file"])
            self.prompts[intent] = ChatPromptTemplate.from_messages([
                ("system", prompt_text),
                ("user", "{query}")
            ])
    
    async def generate_response(self, query: str, intent: str, history: List[Dict[str, str]]) -> str:
        """Generate response based on intent and context"""
        logger.info(f"Generating response for intent: {intent}, query: {query[:50]}...")
        config = self.intent.get(intent)
        if not config:
            for key, value in self.intent.items():
                if value.get("default") == "Yes":
                    logger.warning(f"Unknown intent: {intent}, defaulting to {key}")
                    intent = key
                    config = self.intent[intent]                  
                    break
        try:
            prompt = self.prompts[intent]
            data_type = config["data_source"]["type"]
            if data_type == "vector_db":
                logger.info(f"Processing {intent} intent - getting vector context")
                context = self._get_vector_context(query)
                logger.info(f"Retrieved vector context length: {len(context)}")
            elif data_type == "crawl":
                logger.info(f"Processing {intent} intent - crawling {intent} web")
                url = config["data_source"]["web_url"]
                if not url:
                    logger.error(f"No corresponding web url for {intent} intent")
                    raise ValueError(f"No corresponding web url for {intent} intent")
                context = await crawl_service.crawl_web(url=url)
                logger.info(f"Crawled {intent} web context length: {len(context)}")
            elif data_type == "fixed":
                logger.info(f"Processing {intent} intent - returning fixed content response")
                context = config["data_source"].get("context", "")  
                logger.info(f"Using fixed video response for {intent} intent")
            else:
                logger.error(f"Unknown data source type: {data_type}")
                raise ValueError(f"Unknown data source type: {data_type}")
            
            # Format history
            history_text = ""
            for msg in history[-5:]:  # Only use last 5 messages
                history_text += f"{msg['role']}: {msg['content']}\n"
            
            logger.info(f"Formatted history with {len(history)} messages (using last 5)")
            
            messages = prompt.format_messages(
                query=query,
                context=context,
                history=history_text
            )
            
            # Convert to dict format for LLM service
            message_dicts = [{"role": msg.type, "content": msg.content} for msg in messages]
            
            logger.info("Calling LLM service for response generation")
            response = await self.llm_service.generate_response(message_dicts)
            logger.info(f"Generated response length: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."
    
    async def generate_streaming_response(self, query: str, intent: str, history: List[Dict[str, str]]):
        """Generate streaming response based on intent and context"""
        logger.info(f"Generating streaming response for intent: {intent}, query: {query[:50]}...")
        config = self.intent.get(intent)
        if not config:
            for key, value in self.intent.items():
                if value.get("default") == "Yes":
                    logger.warning(f"Unknown intent: {intent}, defaulting to {key}")
                    intent = key
                    config = self.intent[intent]                  
                    break
        try:
            prompt = self.prompts[intent]
            data_type = config["data_source"]["type"]
            if data_type == "vector_db":
                logger.info(f"Processing {intent} intent - getting vector context")
                context = self._get_vector_context(query)
                logger.info(f"Retrieved vector context length: {len(context)}")
            elif data_type == "crawl":
                logger.info(f"Processing {intent} intent - crawling {intent} web")
                url = config["data_source"]["web_url"]
                if not url:
                    logger.error(f"No corresponding web url for {intent} intent")
                    raise ValueError(f"No corresponding web url for {intent} intent")
                context = await crawl_service.crawl_web(url=url)
                logger.info(f"Crawled {intent} web context length: {len(context)}")
            elif data_type == "fixed":
                logger.info(f"Processing {intent} intent - returning fixed content response")
                context = config["data_source"].get("context", "") 
                logger.info(f"Using fixed video response for {intent} intent")
            else:
                logger.error(f"Unknown data source type: {data_type}")
                raise ValueError(f"Unknown data source type: {data_type}")
            
            # Format history
            history_text = ""
            for msg in history[-5:]:  # Only use last 5 messages
                history_text += f"{msg['role']}: {msg['content']}\n"
            
            logger.info(f"Formatted history with {len(history)} messages (using last 5)")
            
            messages = prompt.format_messages(
                query=query,
                context=context,
                history=history_text
            )
            
            # Convert to dict format for LLM service
            message_dicts = [{"role": msg.type, "content": msg.content} for msg in messages]
            
            logger.info("Starting streaming LLM response generation")
            stream_generator = await self.llm_service.generate_response(message_dicts, stream=True)
            async for chunk in stream_generator:
                yield chunk
            
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}", exc_info=True)
            yield "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."
    
    def _get_vector_context(self, query: str, k: int = 5) -> str:
        """Get relevant context from vector database"""
        try:
            # Search for similar documents
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Combine contexts
            context = ""
            for doc in docs:
                context += f"{doc.page_content}\n\n"
            
            return context.strip()
            
        except Exception as e:
            logger.error(f"Error getting vector context: {e}")
            return ""

class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
        self.embeddings = CustomEmbeddings(
            api_url=settings.embedding_api_url,
            api_key=settings.embedding_api_key
        )
        # Vector store will be initialized when needed
        self.vector_store = None
        self.response_generator = None
    
    def initialize_vector_store(self, intent):
        """Initialize vector store - called during startup"""
        logger.info("Initializing vector store...")
        if self.vector_store is None:
            try:
                if settings.is_postgres:
                    self.vector_store = PGVector(
                        embeddings=self.embeddings,
                        connection=settings.database_url,
                        collection_name=intent,
                        use_jsonb=True,
                    )
                else:
                    self.vector_store = OpenSearchVectorSearch(
                        opensearch_url=settings.opensearch_url,
                        index_name=intent,
                        embedding_function=self.embeddings,
                        verify_certs=False
                    )
                self.response_generator = ResponseGenerator(
                    self.llm_service, 
                    self.embeddings, 
                    self.vector_store
                )
                logger.info("Vector store initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}", exc_info=True)
                raise
        else:
            logger.info("Vector store already initialized")
    
    def get_chat_history(self, db: Session, session_id: str) -> List[Dict[str, str]]:
        """Get chat history for a session"""
        logger.info(f"Getting chat history for session: {session_id}")
        try:
            history = db.query(ChatHistory).filter(
                ChatHistory.session_id == session_id
            ).order_by(ChatHistory.created_at.desc()).limit(10).all()
            
            result = [
                {
                    "role": "user" if msg.message_type == "user" else "assistant",
                    "content": msg.content
                }
                for msg in reversed(history)
            ]
            logger.info(f"Retrieved {len(result)} messages from history for session {session_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting chat history for session {session_id}: {e}", exc_info=True)
            return []
        
    def get_opensearch_chat_history(self, client: OpenSearch, session_id: str) -> List[Dict[str, str]]:
        logger.info(f"Getting chat history from OpenSearch for session: {session_id}")
        try:
            response = client.search(
                index="chat_history",
                body={
                    "size": 10,
                    "sort": [{"created_at": {"order": "desc"}}],
                    "query": {
                        "term": {
                            "session_id": session_id  # dùng keyword nếu cần exact match
                        }
                    }
                }
            )
            
            hits = response["hits"]["hits"]
            result = [
                {
                    "role": "user" if doc["_source"]["message_type"] == "user" else "assistant",
                    "content": doc["_source"]["content"]
                }
                for doc in reversed(hits)  # reverse để giống order_by(created_at asc)
            ]
            logger.info(f"Retrieved {len(result)} messages from OpenSearch for session {session_id}")
            return result
        except Exception as e:
            logger.error(f"Error fetching OpenSearch chat history for session {session_id}: {e}", exc_info=True)
            return []
    
    def save_message(self, db: Session, session_id: str, message_type: str, content: str, intent: str = None):
        """Save message to chat history"""
        logger.info(f"Saving {message_type} message for session {session_id}, intent: {intent}")
        try:
            message = ChatHistory(
                session_id=session_id,
                message_type=message_type,
                content=content,
                intent=intent
            )
            db.add(message)
            db.commit()
            logger.info(f"Successfully saved {message_type} message for session {session_id}")
        except Exception as e:
            logger.error(f"Error saving message for session {session_id}: {e}", exc_info=True)
            db.rollback()
            raise

    def opensearch_save_message(self, client: OpenSearch, session_id: str, message_type: str, content: str, intent: str = None):
        """Save a message to OpenSearch chat history"""
        logger.info(f"Saving {message_type} message to OpenSearch for session {session_id}, intent: {intent}")
        try:
            message_doc = {
                "session_id": session_id,
                "message_type": message_type,
                "content": content,
                "intent": intent,
                "created_at": datetime.now().strftime("%Y%m%d")
            }

            client.index(index="chat_history", body=message_doc)
            logger.info(f"Successfully saved {message_type} message for session {session_id} in OpenSearch")
        except Exception as e:
            logger.error(f"Error saving message for session {session_id} to OpenSearch: {e}", exc_info=True)
            raise

# Global chat service instance
chat_service = ChatService()