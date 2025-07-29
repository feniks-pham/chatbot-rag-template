from typing import List, Dict

from langchain.prompts import ChatPromptTemplate
from langchain_postgres import PGVector
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.database import ChatHistory
from app.services.crawler import crawl_service
from app.services.embeddings import CustomEmbeddings
from app.services.llm import LLMService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ResponseGenerator:
    def __init__(self, llm_service: LLMService, embeddings: CustomEmbeddings, vector_store: PGVector):
        self.llm_service = llm_service
        self.embeddings = embeddings
        self.vector_store = vector_store
        
        # Different prompt templates for each intent
        self.zen_cafe_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một chuyên gia về triết lý và văn hóa cà phê Trung Nguyên Legend.
Hãy trả lời câu hỏi dựa trên thông tin được cung cấp về thiền cà phê và triết lý Trung Nguyên.
Giữ nguyên các nội dung trích dẫn nhưng loại bỏ toàn bộ phần ghi chú tài liệu tham khảo ở cuối câu (ví dụ như: (Thiền Cà Phê Cốt Lõi_Song ngữ Việt Anh_Tài liệu đào tạo (update 21.03.2025))).
Loại bỏ câu này (—This answer was inspired by Coffee Dharma and Trung Nguyên Legend AI—) nếu có trong câu trả lời.
Nếu không có thông tin liên quan trong context, hãy trả lời: "Xin lỗi, tôi không có thông tin về câu hỏi này."

Thông tin tham khảo:
{context}

Lịch sử hội thoại:
{history}"""),
            ("user", "{query}")
        ])
        
        self.location_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là trợ lý hỗ trợ thông tin về địa điểm tổ chức cũng như cách thức đăng ký(đặt vé) trải nghiệm Thiền Cà Phê của Trung Nguyên Legend.
Hãy trả lời câu hỏi dựa trên thông tin địa chỉ tổ chức, cách thức đặt vé được được cung cấp.
Trả lời một cách chính xác, chi tiết và hữu ích.

Thông tin cửa hàng:
{context}

Lịch sử hội thoại:
{history}"""),
            ("user", "{query}")
        ])
        
        self.product_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là tư vấn viên sản phẩm của Trung Nguyên Legend.
Hãy trả lời câu hỏi về sản phẩm, giá cả, menu dựa trên thông tin được cung cấp.
Trả lời một cách nhiệt tình, chi tiết và hữu ích như một nhân viên bán hàng chuyên nghiệp.

Thông tin sản phẩm:
{context}

Lịch sử hội thoại:
{history}"""),
            ("user", "{query}")
        ])
        
        self.philosophy_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là chuyên gia về Cà Phê Triết Đạo và khía cạnh giao hoà Đông Tây trong cà phê của Trung Nguyên Legend.
Khi người dùng hỏi về Cà Phê Triết Đạo, khía cạnh giao hoà Đông Tây, hoặc video về chủ đề này, luôn trả lời:

"Dưới đây là video với chủ đề 'CÀ PHÊ TRIẾT ĐẠO | Cà phê và những ý niệm giao hòa Đông – Tây' mà bạn quan tâm:

Lịch sử hội thoại:
{history}"""),
            ("user", "{query}")
        ])
    
    async def generate_response(self, query: str, intent: str, history: List[Dict[str, str]]) -> str:
        """Generate response based on intent and context"""
        logger.info(f"Generating response for intent: {intent}, query: {query[:50]}...")
        try:
            if intent == "zen_cafe":
                logger.info("Processing zen_cafe intent - getting vector context")
                context = self._get_vector_context(query)
                prompt = self.zen_cafe_prompt
                logger.info(f"Retrieved vector context length: {len(context)}")
            elif intent == "location":
                logger.info("Processing location intent - crawling stores")
                context = await crawl_service.crawl_stores()
                prompt = self.location_prompt
                logger.info(f"Crawled stores context length: {len(context)}")
            elif intent == "product":
                logger.info("Processing product intent - crawling products")
                context = await crawl_service.crawl_products()
                prompt = self.product_prompt
                logger.info(f"Crawled products context length: {len(context)}")
            elif intent == "philosophy":
                logger.info("Processing philosophy intent - returning fixed video response")
                context = ""  # No context needed for philosophy
                prompt = self.philosophy_prompt
                logger.info("Using fixed video response for philosophy intent")
            else:
                logger.warning(f"Unknown intent: {intent}, defaulting to zen_cafe")
                context = self._get_vector_context(query)
                prompt = self.zen_cafe_prompt
            
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
        try:
            if intent == "zen_cafe":
                logger.info("Processing zen_cafe intent - getting vector context")
                context = self._get_vector_context(query)
                prompt = self.zen_cafe_prompt
                logger.info(f"Retrieved vector context length: {len(context)}")
            elif intent == "location":
                logger.info("Processing location intent - crawling stores")
                context = await crawl_service.crawl_stores()
                prompt = self.location_prompt
                logger.info(f"Crawled stores context length: {len(context)}")
            elif intent == "product":
                logger.info("Processing product intent - crawling products")
                context = await crawl_service.crawl_products()
                prompt = self.product_prompt
                logger.info(f"Crawled products context length: {len(context)}")
            elif intent == "philosophy":
                logger.info("Processing philosophy intent - returning fixed video response")
                # For philosophy intent, we deliver a single fixed response without streaming
                response = "Dưới đây là video với chủ đề \"CÀ PHÊ TRIẾT ĐẠO | Cà phê và những ý niệm giao hòa Đông – Tây\" mà bạn quan tâm:\n"
                yield response
                return
            else:
                logger.warning(f"Unknown intent: {intent}, defaulting to zen_cafe")
                context = self._get_vector_context(query)
                prompt = self.zen_cafe_prompt
            
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
    
    def initialize_vector_store(self):
        """Initialize vector store - called during startup"""
        logger.info("Initializing vector store...")
        if self.vector_store is None:
            try:
                self.vector_store = PGVector(
                    embeddings=self.embeddings,
                    connection=settings.database_url,
                    collection_name="qa_embeddings",
                    use_jsonb=True,
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

# Global chat service instance
chat_service = ChatService()
