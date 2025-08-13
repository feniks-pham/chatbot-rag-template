from datetime import datetime
from uuid import uuid4
from opensearchpy import OpenSearch
from urllib.parse import urlparse

from app.config.settings import settings

def get_opensearch_db():
    parsed = urlparse(settings.opensearch_url)
    host = parsed.hostname        
    port = parsed.port              
    username = parsed.username      
    password = parsed.password      

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=False
    )
    try:
        yield client
    finally:
        client.close()

def create_indices():
    parsed = urlparse(settings.opensearch_url)
    host = parsed.hostname        
    port = parsed.port              
    username = parsed.username      
    password = parsed.password      

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=False
    )
    # sessions index
    if not client.indices.exists(index="sessions"):
        client.indices.create(
            index="sessions",
            body={
                "mappings": {
                    "properties": {
                        "id": { "type": "keyword" },
                        "created_at": { "type": "date" },
                        "updated_at": { "type": "date" }
                    }
                }
            }
        )
    # chat_history index
    if not client.indices.exists(index="chat_history"):
        client.indices.create(
            index="chat_history",
            body={
                "mappings": {
                    "properties": {
                        "id": { "type": "integer" },
                        "session_id": { "type": "keyword" },
                        "message_type": { "type": "keyword" },
                        "content": { "type": "text" },
                        "intent": { "type": "keyword" },
                        "created_at": { "type": "date" }
                    }
                }
            }
        )