from datetime import datetime
from uuid import uuid4
from opensearchpy import OpenSearch

from app.config.settings import settings

client = OpenSearch(
    hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
    http_auth=(settings.opensearch_user, settings.opensearch_initial_admin_password),
    use_ssl=True,
    verify_certs=False
)

def get_opensearch_db():
    client = OpenSearch(
        hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
        http_auth=(settings.opensearch_user, settings.opensearch_initial_admin_password),
        use_ssl=True,
        verify_certs=False
    )
    try:
        yield client
    finally:
        client.close()

def create_indices():
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