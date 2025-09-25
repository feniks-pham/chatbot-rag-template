import sys
import os
import re
import json
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

BATCH_SIZE = 16  # có thể chỉnh 8/12/16 tùy server

def _batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# --- helper để parse header từ các chunk PDF ---
_PDF_HEADER_RE = re.compile(
    r"^\[(?P<src>PDF(?:\s+p\.(?P<page>\d+))?\s*-\s*(?P<section>text|table))\]\s*\n",
    re.IGNORECASE,
)
_TABLE_META_RE = re.compile(r"^\[TABLE_META\](\{.*?\})\s*\n", re.DOTALL)

def _strip_pdf_header_and_meta(text: str):
    """
    Nếu chunk bắt đầu bằng header dạng:
      [PDF p.3 - text]\n...
      [PDF p.10 - table]\n...
      [PDF - table]\n...
    -> Loại header và trích meta (page, section_type).
    """
    m = _PDF_HEADER_RE.match(text or "")
    if not m:
        return text, None, None
    page = m.group("page")
    section = m.group("section")
    clean = text[m.end():].strip()
    return clean, (int(page) if page else None), (section.lower() if section else None)

def _pop_table_meta(text: str):
    """
    Nếu chunk bắt đầu bằng:
      [TABLE_META]{...json}\n
    -> cắt bỏ dòng này và trả ra (clean_text, meta_dict). Ngược lại trả (text, None).
    """
    m = _TABLE_META_RE.match(text or "")
    if not m:
        return text, None
    try:
        meta = json.loads(m.group(1))
    except Exception:
        meta = None
    clean = text[m.end():].strip()
    return clean, meta

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
                file_type = os.path.splitext(filename)[1].lower()    
                if settings.is_prod:
                    logger.info("Loading Q&A data from S3 (Production mode)...")
                    s3_service = S3Service()
                    data = asyncio.run(s3_service.load_qa_data(filename=filename, file_type=file_type))
                else:
                    logger.info("Loading Q&A data from local file (Development mode)...")
                    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                    file_path = os.path.join(data_path, filename) 
                    local_data_service = LocalDataService()
                    data = asyncio.run(local_data_service.load_qa_data(data_file=file_path, file_type=file_type))
                    
                logger.info(f"Loaded {filename} file successfully")
                    
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
                        http_auth=(settings.opensearch_username, settings.opensearch_password),
                        verify_certs=False
                    )
                    
                # Prepare documents for embedding
                logger.info("Preparing documents...")
                documents = []
                metadatas = []

                if file_type in [".xls", ".xlsx"]:                    
                    for i, qa in enumerate(data):
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
                            "source": "xlsx",
                            "tokens": token_count,
                            "created_at": datetime.now().isoformat()
                        })
                            
                        if (i + 1) % 10 == 0:
                            logger.info(f"Processed {i + 1}/{len(data)} documents")
                        
                    # # Add documents to vector store
                    # logger.info("Adding documents to vector store...")
                    # vector_store.add_texts(
                    #     texts=documents,
                    #     metadatas=metadatas
                    # )
                        
                    # logger.info(f"Successfully imported {len(documents)} Q&A pairs to vector database")

                elif file_type == ".md":
                    for i, chunk in enumerate(data):
                        document_content = chunk
                        # Count tokens
                        tokens = tokenizer.encode(document_content, add_special_tokens=False)
                        token_count = len(tokens)

                        documents.append(document_content)
                        metadatas.append({
                            "type": intent,
                            "source": "md",
                            "tokens": token_count,
                            "created_at": datetime.now().isoformat()
                        })

                        if (i + 1) % 10 == 0:
                            logger.info(f"Processed {i + 1}/{len(data)} md-chunks")

                elif file_type == ".pdf":
                     # data: list[str] các chunk có header [PDF p.X - text/table] và có thể có dòng [TABLE_META]{...}
                    for i, raw_chunk in enumerate(data):
                        # 1) cắt header PDF để lấy page/section_type
                        cleaned, page, section_type = _strip_pdf_header_and_meta(raw_chunk)
                        document_content = cleaned if cleaned else raw_chunk

                        # 2) nếu có TABLE_META ở đầu, lấy meta + bỏ khỏi nội dung
                        document_content, table_meta = _pop_table_meta(document_content)

                        # 3) đếm tokens cho nội dung embed
                        tokens = tokenizer.encode(document_content, add_special_tokens=False)
                        token_count = len(tokens)

                        # 4) metadata
                        meta_entry = {
                            "type": intent,
                            "source": "pdf",
                            "page": (table_meta.get("page") if table_meta and table_meta.get("page") is not None else page),
                            "section_type": section_type,  # 'text' hoặc 'table'
                            "tokens": token_count,
                            "created_at": datetime.now().isoformat()
                        }
                        if table_meta:
                            meta_entry.update({
                                "table_n_rows": table_meta.get("n_rows"),
                                "table_n_cols": table_meta.get("n_cols"),
                                "table_columns": table_meta.get("columns"),
                            })

                        documents.append(document_content)
                        metadatas.append(meta_entry)

                        if (i + 1) % 10 == 0:
                            logger.info(f"Processed {i + 1}/{len(data)} pdf-chunks")
                else:
                    logger.warning(f"Unsupported file type for {filename}: {file_type}. Skipping.")
                    continue

                # Add documents to vector store
                logger.info("Adding documents to vector store in batches...")
                total = len(documents)
                added = 0
                for texts_batch, metas_batch in zip(_batched(documents, BATCH_SIZE), _batched(metadatas, BATCH_SIZE)):
                    vector_store.add_texts(texts=texts_batch, metadatas=metas_batch)
                    added += len(texts_batch)
                    logger.info(f"Added {added}/{total} to vector store")

                logger.info(f"Successfully imported {len(documents)} items to vector database")

        
    except Exception as e:
        logger.error(f"Error importing Q&A data: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import_qa_data()
