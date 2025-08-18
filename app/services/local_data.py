import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from typing import List, Dict
from app.config.settings import settings
from app.utils.logger import get_logger
from langchain_text_splitters import MarkdownTextSplitter
from transformers import AutoTokenizer

logger = get_logger(__name__)

class LocalDataService:
    def __init__(self):
        logger.info(f"LocalDataService initialized with file in data folder")
    
    async def load_qa_data(self, data_file, file_type) -> List[Dict[str, str]]:
        """Load Q&A data from local Excel file"""
        try:
            logger.info(f"Loading Q&A data from local file: {data_file}")

            if file_type in [".xls", ".xlsx"]:
                # Read Excel file
                excel_data = pd.read_excel(data_file)
                
                logger.info(f"Excel file loaded with {len(excel_data)} rows")
                
                # Convert to list of dicts (same format as S3 service)
                qa_data = []
                for _, row in excel_data.iterrows():
                    if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):  # Skip if question or answer is NaN
                        qa_data.append({
                            'question': str(row.iloc[1]).strip(),  # Column B (index 1)
                            'answer': str(row.iloc[2]).strip()     # Column C (index 2)
                        })
                
                logger.info(f"Successfully processed {len(qa_data)} Q&A pairs from local file")
                return qa_data
            
            elif file_type == ".md":
                with open(data_file, "r", encoding="utf-8") as f:
                    md_data = f.read()

                logger.info(f"Markdown file {data_file} loaded")
                tokenizer = AutoTokenizer.from_pretrained(settings.embedding_model_name, token=settings.hf_token, trust_remote_code=True)
                splitter = MarkdownTextSplitter.from_huggingface_tokenizer(tokenizer=tokenizer, chunk_size=settings.embedding_max_tokens, chunk_overlap=settings.embedding_max_tokens/5)
                data = splitter.split_text(md_data)
                logger.info(f"Successfully processed {len(data)} chunks from local file")
                return data
            
        except FileNotFoundError:
            logger.error(f"Local data file not found: {data_file}")
            raise Exception(f"Local data file not found: {data_file}")
        except Exception as e:
            logger.error(f"Error loading Q&A data from local file: {str(e)}")
            raise Exception(f"Failed to Q&A load data from local file: {str(e)}")