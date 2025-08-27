import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain.prompts import ChatPromptTemplate
from app.services.llm import LLMService
from app.core.intent_router import IntentRouter
from app.core.chat_service import chat_service
from app.utils.load_intents import load_prompt_template

llm_service = LLMService()
intent_router = IntentRouter(llm_service)

async def non_rag_response(query: str): 
    with open("evaluation/non-rag-prompt.txt", "r", encoding="utf-8") as f:
        prompt_text = f.read()
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "{query}")
    ])
    messages = prompt.format_messages(
        query=query
    )
    message_dicts = [{"role": msg.type, "content": msg.content} for msg in messages]
    response = await llm_service.generate_response(message_dicts)
    return response

async def rag_response(query: str):
    intent = await intent_router.classify_intent(query)
    chat_service.initialize_vector_store(intent)
    response = await chat_service.response_generator.generate_response(
        query=query, intent=intent, history=[]
    )
    return response


