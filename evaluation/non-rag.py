import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain.prompts import ChatPromptTemplate

async def non_rag_response(query: str): 
    with open("evaluation/non-rag-prompt.txt", "r", encoding="utf-8") as f:
        prompt_text = f.read()
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "{query}")
    ])