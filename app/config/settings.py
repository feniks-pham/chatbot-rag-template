import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    app_env: str = "dev"  # dev or prod
    
    # Database
    database_url: str
    
    # S3 (only for prod)
    s3_path: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_endpoint_url: str = ""
    s3_excel_file_key: str = ""
    
    # Local data (only for dev)
    local_data_file: str = "data/trung-nguyen-legend.xlsx"
    
    # LLM
    llm_api_url: str
    llm_api_key: str
    llm_model: str = "gemini-2.0-flash"

    # TTS
    tts_api_url: str
    tts_api_key: str
    tts_model: str = "zalo-tts-vi"
    tts_speaker_id: int = 1
    tts_speed: float = 1.0
    tts_encode_type: int = 1

    # Embedding
    embedding_api_url: str
    embedding_api_key: str
    embedding_model_name: str
    embedding_max_tokens: int

    # Huggingface
    hf_token: str

    # Application
    log_level: str = "INFO"
    log_dir: str = "~/logs/trung-nguyen-chatbot"
    
    # Crawl URLs
    store_url: str
    product_url: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_dev(self) -> bool:
        """Check if running in development environment"""
        return self.app_env.lower() == "dev"
    
    @property
    def is_prod(self) -> bool:
        """Check if running in production environment"""
        return self.app_env.lower() == "prod"
    
    def model_post_init(self, __context) -> None:
        """Validate environment-specific configurations"""
        if self.is_prod:
            # Production requires S3 settings
            required_s3_fields = [
                's3_path', 'aws_access_key_id', 'aws_secret_access_key', 
                's3_endpoint_url', 's3_excel_file_key'
            ]
            for field in required_s3_fields:
                if not getattr(self, field):
                    raise ValueError(f"Production environment requires {field} to be set")
        elif self.is_dev:
            # Development requires local data file
            if not os.path.exists(self.local_data_file):
                raise ValueError(f"Development environment requires local data file at {self.local_data_file}")

settings = Settings()
