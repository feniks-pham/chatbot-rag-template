import sys
import os
from datetime import datetime
from transformers import AutoTokenizer
from langchain_postgres import PGVector
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.s3 import S3Service
from app.services.local_data import LocalDataService
from app.services.embeddings import CustomEmbeddings
from app.config.settings import settings
from app.utils.logger import get_logger
from app.utils.load_intents import load_intents
from app.utils.create_db import create_db_if_not_exists
logger = get_logger(__name__)

def import_qa_data():
    """Import Q&A data from S3 (prod) or local file (dev) to vector database"""
    try:
        logger.info("Starting Q&A data import...")
        logger.info(f"Environment: {settings.app_env}")
        
        # Load data based on environment
        import asyncio

        # Initialize embeddings
        logger.info("Initializing embeddings...")
        embeddings = CustomEmbeddings(
            api_url=settings.embedding_api_url,
            api_key=settings.embedding_api_key
        ) 
                      
        # Initialize tokenizer for token counting
        logger.info("Initializing tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(settings.embedding_model_name, token=settings.hf_token, trust_remote_code=True)

        intents = load_intents()
        for intent, config in intents.items():
            if config["data_source"].get("file"): 
                filename = config["data_source"].get("file")    
                if settings.is_prod:
                    logger.info("Loading Q&A data from S3 (Production mode)...")
                    s3_service = S3Service()
                    qa_data = asyncio.run(s3_service.load_qa_data(filename))
                else:
                    logger.info("Loading Q&A data from local file (Development mode)...")
                    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                    file_path = os.path.join(data_path, filename) 
                    local_data_service = LocalDataService()
                    qa_data = asyncio.run(local_data_service.load_qa_data(file_path))
                    
                logger.info(f"Loaded {len(qa_data)} Q&A pairs")
                    
                # Initialize vector store
                logger.info("Initializing vector store...")
                if settings.is_postgres:
                    create_db_if_not_exists(settings.database_url)
                    vector_store = PGVector(
                        embeddings=embeddings,
                        connection=settings.database_url,
                        collection_name=intent,
                        use_jsonb=True,
                    )
                else:
                    vector_store = OpenSearchVectorSearch(
                        opensearch_url=settings.opensearch_url,
                        index_name=intent,
                        embedding_function=embeddings,
                        verify_certs=False
                    )
                    
                # Prepare documents for embedding
                logger.info("Preparing documents...")
                documents = []
                metadatas = []
                    
                for i, qa in enumerate(qa_data):
                    # Create document with question and answer combined
                    document_content = f"Câu hỏi: {qa['question']}\nCâu trả lời: {qa['answer']}"
                        
                    # Count tokens using tokenizer
                    tokens = tokenizer.encode(document_content, add_special_tokens=False)
                    token_count = len(tokens)
                        
                    documents.append(document_content)
                    metadatas.append({
                        "question": qa['question'],
                        "answer": qa['answer'],
                        "type": intent,
                        "tokens": token_count,
                        "created_at": datetime.now().isoformat()
                    })
                        
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{len(qa_data)} documents")
                    
                # Add documents to vector store
                logger.info("Adding documents to vector store...")
                vector_store.add_texts(
                    texts=documents,
                    metadatas=metadatas
                )
                    
                logger.info(f"Successfully imported {len(documents)} Q&A pairs to vector database")
        
    except Exception as e:
        logger.error(f"Error importing Q&A data: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import_qa_data()
