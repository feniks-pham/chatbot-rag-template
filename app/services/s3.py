import threading

import boto3
import pandas as pd
from io import BytesIO
from typing import List, Dict
from botocore.exceptions import ClientError
from transformers import AutoTokenizer
from langchain_text_splitters import MarkdownTextSplitter
from app.config.settings import settings
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

class S3Service:
    def __init__(self):
        self.thread_local = threading.local()
        self.bucket = settings.s3_path
        s3_config = {
            'aws_access_key_id': settings.aws_access_key_id,
            'aws_secret_access_key': settings.aws_secret_access_key,
            'endpoint_url': settings.s3_endpoint_url,
            'verify': True,
        }
        try:
            if not hasattr(self.thread_local, 's3_client'):
                self.thread_local.s3_client = boto3.client('s3', **s3_config)
            self.thread_local.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"Successfully connected to S3 bucket: {self.bucket}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to connect to S3: {error_code} - {error_message}")
            raise Exception(f"Failed to connect to S3: {error_message}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to S3: {str(e)}")
            raise Exception(f"Unexpected error connecting to S3: {str(e)}")
    
    @property
    def s3_client(self):
        """Get thread-local S3 client"""
        if not hasattr(self.thread_local, 's3_client'):
            s3_config = {
                'aws_access_key_id': settings.aws_access_key_id,
                'aws_secret_access_key': settings.aws_secret_access_key,
                'endpoint_url': settings.s3_endpoint_url,
                'verify': True,
            }
            self.thread_local.s3_client = boto3.client('s3', **s3_config)
        return self.thread_local.s3_client
    
    async def load_qa_data(self, filename, file_type) -> List[Dict[str, str]]:
        """Load Q&A data from Excel file in S3"""
        try:
            logger.info(f"Loading Q&A data from S3: {self.bucket}/{filename}")
            
            # Download file from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=filename
            )
            
            logger.info("Successfully downloaded file from S3")
            
            if file_type in [".xls", ".xlsx"]:
                # Read Excel file
                excel_data = pd.read_excel(BytesIO(response['Body'].read()))
                
                logger.info(f"Excel file loaded with {len(excel_data)} rows")
                
                # Convert to list of dicts
                qa_data = []
                for _, row in excel_data.iterrows():
                    if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):  # Skip if question or answer is NaN
                        qa_data.append({
                            'question': str(row.iloc[1]).strip(),  # Column B (index 1)
                            'answer': str(row.iloc[2]).strip()     # Column C (index 2)
                        })
                
                logger.info(f"Successfully processed {len(qa_data)} Q&A pairs")
                return qa_data
            
            elif file_type == ".md":
                # Read Markdown file
                md_data = response['Body'].read().decode("utf-8")

                logger.info(f"Markdown file {filename} loaded")
                tokenizer = AutoTokenizer.from_pretrained(settings.embedding_model_name, token=settings.hf_token, trust_remote_code=True)
                splitter = MarkdownTextSplitter.from_huggingface_tokenizer(tokenizer=tokenizer, chunk_size=settings.embedding_max_tokens, chunk_overlap=settings.embedding_max_tokens/5)
                data = splitter.split_text(md_data)
                logger.info(f"Successfully processed {len(data)} chunks from local file")
                return data
           
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"S3 ClientError loading Q&A data: {error_code} - {error_message}")
            raise Exception(f"Failed to load Q&A data from S3: {error_message}")
        except Exception as e:
            logger.error(f"Unexpected error loading Q&A data: {str(e)}")
            raise Exception(f"Failed to load Q&A data from S3: {str(e)}")
