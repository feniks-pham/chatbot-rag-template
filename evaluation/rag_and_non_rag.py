import os
import sys
import asyncio
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics._factual_correctness import FactualCorrectness
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from app.config.settings import settings
from evaluation.llm_response import non_rag_response, rag_response

os.environ["OPENAI_API_KEY"] = settings.evaluation_llm_api_key

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
wrapped_llm = LangchainLLMWrapper(llm)
scorer = FactualCorrectness(llm=wrapped_llm)

with open("evaluation/testcases.json", "r", encoding="utf-8") as f:
    data = json.load(f)
testcases = data["testcase"]


def non_rag_evaluation():
    total_score = 0
    score_list = []
    for tc in testcases:
        query = tc["query"]
        answer = tc["sample answer"]
        response = asyncio.run(non_rag_response(query))
        sample = SingleTurnSample(
            response=response,
            reference=answer
        )
        score = asyncio.run(scorer.single_turn_ascore(sample))
        score_list.append(score) 
        total_score += score
    for idx, score in enumerate(score_list):
        print(f"Testcase {idx+1} Non Rag Response Score: {score}\n")
    avg_score = total_score / len(testcases)
    print(f"Non Rag Response Average Score: {avg_score}\n")
    return avg_score

def rag_evaluation():
    total_score = 0
    score_list = []
    for tc in testcases:
        query = tc["query"]
        answer = tc["sample answer"]
        response = asyncio.run(rag_response(query)) 
        sample = SingleTurnSample(
            response=response,
            reference=answer
        )
        score = asyncio.run(scorer.single_turn_ascore(sample))
        score_list.append(score) 
        total_score += score
    for idx, score in enumerate(score_list):
        print(f"Testcase {idx+1} Rag Response Score: {score}")
    avg_score = total_score / len(testcases)
    print(f"Rag Response Average Score: {avg_score}")
    return avg_score

if __name__ == "__main__":
    non_rag_evaluation()
    rag_evaluation()




    
    


