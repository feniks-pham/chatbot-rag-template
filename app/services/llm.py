import httpx
from typing import List, Dict, Any, AsyncGenerator
import json
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        self.api_url = settings.llm_api_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate response from LLM"""

        # Convert messages to Gemini format and fix roles
        normalized_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            # Only convert "human" role to "user", keep "system" and "assistant" unchanged
            if role == "human":
                role = "user"
            
            normalized_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })

        payload = {
            "model": self.model,
            "messages": normalized_messages,
            "stream": stream,
            "temperature": 0.0,
        }
        
        if stream:
            logger.info("Starting streaming response")
            return self._stream_response(payload)
        else:
            async with httpx.AsyncClient() as client:
                logger.info("Making non-streaming LLM request")
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                logger.info(f"LLM response status: {response.status_code}")
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                    raise Exception(f"LLM API error: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    logger.error(f"Unexpected error occurred: {str(e)}")
                    raise Exception(f"Unexpected error when calling LLM API: {str(e)}")
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"LLM response length: {len(content)}")
                return content
    
    async def _stream_response(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream response from LLM"""
        logger.info("Starting streaming response from LLM")
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30.0
            ) as response:
                logger.info(f"Streaming response status: {response.status_code}")
                response.raise_for_status()
                chunk_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            logger.info(f"Stream completed after {chunk_count} chunks")
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    chunk_count += 1
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON chunk: {data}")
                            continue