import pandas as pd
from typing import List, Dict
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LocalDataService:
    def __init__(self):
        self.data_file = settings.local_data_file
        logger.info(f"LocalDataService initialized with file: {self.data_file}")
    
    async def load_qa_data(self) -> List[Dict[str, str]]:
        """Load Q&A data from local Excel file"""
        try:
            logger.info(f"Loading Q&A data from local file: {self.data_file}")
            
            # Read Excel file
            excel_data = pd.read_excel(self.data_file)
            
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
            
        except FileNotFoundError:
            logger.error(f"Local data file not found: {self.data_file}")
            raise Exception(f"Local data file not found: {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading Q&A data from local file: {str(e)}")
            raise Exception(f"Failed to load Q&A data from local file: {str(e)}")