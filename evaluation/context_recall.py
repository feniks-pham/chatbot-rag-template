import os
import sys
import asyncio
import json
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import LLMContextRecall
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from app.config.settings import settings
from app.core.chat_service import chat_service
from app.services.llm import LLMService
from app.core.intent_router import IntentRouter

os.environ["OPENAI_API_KEY"] = settings.evaluation_llm_api_key

llm_service = LLMService()
intent_router = IntentRouter(llm_service)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
wrapped_llm = LangchainLLMWrapper(llm)
context_recall = LLMContextRecall(llm=wrapped_llm)

with open("evaluation/testcases.json", "r", encoding="utf-8") as f:
    data = json.load(f)
testcases = data["testcase"]

def context_recall_evaluation():
    total_score = 0
    score_list = []
    for tc in testcases:
        query = tc["query"]
        answer = tc["sample answer"]
        intent = asyncio.run(intent_router.classify_intent(query)) 
        chat_service.initialize_vector_store(intent)
        docs = chat_service.vector_store.similarity_search(query)
        retrieved_contexts = []
        for doc in docs:
            retrieved_contexts.append(doc.page_content)
        response = asyncio.run(chat_service.response_generator.generate_response(
            query=query, intent=intent, history=[]
        )) 
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            reference=answer,
            retrieved_contexts=retrieved_contexts
        )
        score = asyncio.run(context_recall.single_turn_ascore(sample))
        score_list.append(score)
        total_score += score
    for idx, score in enumerate(score_list):
        print(f"Testcase {idx+1} Context Recall Score: {score}\n")
    avg_score = total_score / len(testcases)
    print(f"Context Recall Average Score: {avg_score}\n")
    return 

if __name__ == "__main__":
    context_recall_evaluation()

