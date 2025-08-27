import os
import sys
import asyncio
import json
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ragas import SingleTurnSample 
from ragas.metrics import ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from app.config.settings import settings
from app.core.chat_service import chat_service
from app.services.embeddings import CustomEmbeddings
from app.services.llm import LLMService
from app.core.intent_router import IntentRouter

os.environ["OPENAI_API_KEY"] = settings.evaluation_llm_api_key

llm_service = LLMService()
intent_router = IntentRouter(llm_service)

embeddings=LangchainEmbeddingsWrapper(CustomEmbeddings(api_url=settings.embedding_api_url, api_key=settings.embedding_api_key))
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
wrapped_llm = LangchainLLMWrapper(llm)
scorer = ResponseRelevancy(llm=wrapped_llm, embeddings=embeddings)

with open("evaluation/testcases.json", "r", encoding="utf-8") as f:
    data = json.load(f)
testcases = data["testcase"]

def response_relevancy_evaluation():
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
            response=str(response),
            retrieved_contexts=retrieved_contexts
        )
        score = asyncio.run(scorer.single_turn_ascore(sample))
        score_list.append(score)
        total_score += score
    for idx, score in enumerate(score_list):
        print(f"Testcase {idx+1} Response Relevancy Score: {score}\n")
    avg_score = total_score / len(testcases)
    print(f"Response Relevancy Average Score: {avg_score}\n")
    return avg_score

if __name__ == "__main__":
    response_relevancy_evaluation()


