import json
from typing import List

import httpx
from langchain.embeddings.base import Embeddings

from app.utils.logger import get_logger

logger = get_logger(__name__)

def split_text_by_token_count(text: str, max_tokens: int = 512, overlap: int = 0) -> List[str]:
    """Simple text chunking by character count (approximation for tokens)"""
    # Rough approximation: 1 token ≈ 4 characters for most languages
    max_chars = max_tokens * 4
    overlap_chars = overlap * 4
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk_text = text[start:end]
        chunks.append(chunk_text)
        if end >= len(text):
            break
        start += max_chars - overlap_chars
    return chunks

class CustomEmbeddings(Embeddings):
    """Custom embedding class using API"""
    
    def __init__(self, api_url: str, api_key: str, model_name: str = None, max_tokens: int = None):
        from app.config.settings import settings
        
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name or settings.embedding_model_name
        self.max_tokens = max_tokens or settings.embedding_max_tokens
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        try:
            # Process and chunk texts
            chunked_texts = []
            for text in texts:
                chunks = split_text_by_token_count(text, self.max_tokens, 0)
                chunked_texts.append(chunks[0])  # Take first chunk
            
            payload = {
                "input": chunked_texts,
                "model": self.model_name
            }
            
            json_payload = json.dumps(payload, ensure_ascii=False)
            
            # Synchronous request using httpx
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.api_url,
                    headers=self.headers,
                    content=json_payload,
                )
                response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            logger.info(f"[Embeddings Response] | content={texts[0][:100]} | tokens={response_data.get('usage', {}).get('prompt_tokens', 'N/A')}")
            
            embeddings = []
            for item in response_data["data"]:
                embeddings.append(item["embedding"])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"API Embedding Error: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response Body: {e.response.text}")
            raise e
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        logger.info(f"[Embeddings Query] | model={self.model_name} | text={text[:100]}...")
        return self.embed_documents([text])[0]
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async version of embed_documents"""
        try:
            # Process and chunk texts
            chunked_texts = []
            for text in texts:
                chunks = split_text_by_token_count(text, self.max_tokens, 0)
                chunked_texts.append(chunks[0])  # Take first chunk
            
            payload = {
                "input": chunked_texts,
                "model": self.model_name
            }
            
            json_payload = json.dumps(payload, ensure_ascii=False)
            
            # Async request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    content=json_payload,
                )
                response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            logger.info(f"[Async Embeddings Response] | content={texts[0][:100]} | tokens={response_data.get('usage', {}).get('prompt_tokens', 'N/A')}")
            
            embeddings = []
            for item in response_data["data"]:
                embeddings.append(item["embedding"])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Async API Embedding Error: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response Body: {e.response.text}")
            raise e
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async version of embed_query"""
        logger.info(f"[Async Embeddings Query] | model={self.model_name} | text={text[:100]}...")
        result = await self.aembed_documents([text])
        return result[0]
