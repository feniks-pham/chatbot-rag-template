from typing import List, Dict

from langchain.prompts import ChatPromptTemplate

from app.services.llm import LLMService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class IntentRouter:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một hệ thống phân loại ý định cho chatbot cafe Trung Nguyên.
Hãy phân loại câu hỏi của người dùng vào một trong ba loại sau:

1. "location" - Câu hỏi về địa chỉ tổ chức, vị trí, số điện thoại, thời gian tổ chức trải nghiệm thiền cà phê
   Ví dụ: "Địa chỉ tổ chức thiền cà phê của Trung Nguyên Legend", "Số điện thoại và cách đặt vé trải nghiệm thiền cà phê?", "Thời gian tổ chức trải nghiệm thiền cà phê là khi nào?"

2. "product" - Câu hỏi về sản phẩm, giá cả, menu, loại cà phê
   Ví dụ: "Giá cà phê espresso bao nhiêu?", "Có những loại bộ sản phẩm nào?"

3. "zen_cafe" - Tất cả các câu hỏi khác, đặc biệt về triết lý, văn hóa, thiền cafe
   Ví dụ: "Thiền cafe là gì?", "Triết lý của Trung Nguyên?"

Chỉ trả lời bằng một từ: location, product, hoặc zen_cafe"""),
            ("user", "Câu hỏi: {query}")
        ])
    
    async def classify_intent(self, query: str) -> str:
        """Classify user query into intent categories"""
        logger.info(f"Classifying intent for query: {query[:50]}...")
        try:
            messages = self.intent_prompt.format_messages(query=query)
            # Convert to dict format for LLM service
            message_dicts = [{"role": msg.type, "content": msg.content} for msg in messages]
            
            logger.info("Calling LLM for intent classification")
            response = await self.llm_service.generate_response(message_dicts)
            intent = response.strip().lower()
            
            # Validate intent
            if intent in ["location", "product", "philosophy", "zen_cafe"]:
                logger.info(f"Intent classified as: {intent}")
                return intent
            else:
                logger.warning(f"Invalid intent '{intent}', defaulting to zen_cafe")
                return "zen_cafe"  # Default fallback
                
        except Exception as e:
            logger.error(f"Error in intent classification: {e}", exc_info=True)
            return "zen_cafe"  # Default fallback

class QueryRewriter:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý AI giúp viết lại câu hỏi dựa trên lịch sử hội thoại.
Nhiệm vụ của bạn là:
1. Nếu câu hỏi hiện tại đã rõ ràng và đầy đủ, giữ nguyên
2. Nếu câu hỏi thiếu context hoặc mơ hồ, kết hợp với lịch sử để làm rõ
3. Chỉ trả về câu hỏi đã được viết lại, không giải thích thêm

Ví dụ:
- Lịch sử: "Tôi muốn biết về cà phê espresso"
- Câu hỏi mới: "Giá bao nhiêu?"
- Kết quả: "Giá cà phê espresso bao nhiêu?"

Lịch sử hội thoại:
{history}

Câu hỏi hiện tại: {query}

Câu hỏi đã viết lại:"""),
            ("user", "{query}")
        ])
    
    async def rewrite_query(self, query: str, history: List[Dict[str, str]]) -> str:
        """Rewrite query based on conversation history"""
        try:
            # Format history
            history_text = ""
            for msg in history[-5:]:  # Only use last 5 messages
                history_text += f"{msg['role']}: {msg['content']}\n"
            
            messages = self.rewrite_prompt.format_messages(
                query=query,
                history=history_text
            )
            # Convert to dict format for LLM service
            message_dicts = [{"role": msg.type, "content": msg.content} for msg in messages]
            
            rewritten_query = await self.llm_service.generate_response(message_dicts)
            rewritten_result = rewritten_query.strip()
            
            logger.info(f"Query rewritten from '{query}' to '{rewritten_result}'")
            return rewritten_result
            
        except Exception as e:
            logger.error(f"Error in query rewriting: {e}", exc_info=True)
            logger.info("Returning original query due to error")
            return query  # Return original query if rewriting fails
