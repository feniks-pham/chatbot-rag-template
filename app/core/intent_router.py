import os
from typing import List, Dict

from langchain.prompts import ChatPromptTemplate

from app.services.llm import LLMService
from app.utils.logger import get_logger
from app.utils.load_intents import load_prompt_template

logger = get_logger(__name__)


class IntentRouter:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.intent_prompt = ChatPromptTemplate.from_messages([
            ("system", load_prompt_template("intent_prompt.txt")),
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
            ("system", load_prompt_template("rewrite_prompt.txt")),
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
