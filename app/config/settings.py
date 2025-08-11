import os
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Environment
    app_env: str = "dev"  # dev or prod
    database: str = "postgres" # postgres or opensearch
    
    # Database (postgres)
    database_url: str = ""

    # Database (opensearch)
    opensearch_url: str = ""
    
    # S3 (only for prod)
    s3_path: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_endpoint_url: str = ""
    
    # LLM
    llm_api_url: str
    llm_api_key: str
    llm_model: str = "gpt-4o-mini"

    # TTS
    tts_api_url: str
    tts_api_key: str
    tts_model: str = "zalo-tts-vi"
    tts_speaker_id: int = 1
    tts_speed: float = 1.0
    tts_encode_type: int = 1

    # Gemini TTS
    gemini_tts_api_url: str
    gemini_tts_api_key: str
    gemini_tts_voice_language_code: str = "vi-VN"
    gemini_tts_voice_name: str = "vi-VN-Standard-C"
    gemini_tts_audio_encoding: str = "MP3"
    gemini_tts_speaking_rate: float = 1.0
    gemini_tts_pitch: float = 0.0
    gemini_tts_sample_rate_hertz: int = 24000

    # STT
    # stt_api_url: str
    # stt_api_key: str
    # stt_model: str = "zalo-stt-vi"
    # stt_encoding_type: str = "mp3"

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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("database")
    @classmethod
    def validate_database(cls, value):
        allowed = {"postgres", "opensearch"}
        if value.lower() not in allowed:
            raise ValueError(f"Invalid database: {value}. Must be one of {allowed}")
        return value.lower()
    
    @property
    def is_dev(self) -> bool:
        """Check if running in development environment"""
        return self.app_env.lower() == "dev"
    
    @property
    def is_prod(self) -> bool:
        """Check if running in production environment"""
        return self.app_env.lower() == "prod"
    
    @property
    def is_postgres(self) -> bool:
        """Check if using postgres database"""
        return self.database.lower() == "postgres"
    
    @property
    def is_opensearch(self) -> bool:
        """Check if using opensearch database"""
        return self.database.lower() == "opensearch"
    
    def model_post_init(self, __context) -> None:
        """Validate environment-specific configurations"""
        if self.is_prod:
            # Production requires S3 settings
            required_s3_fields = [
                's3_path', 'aws_access_key_id', 'aws_secret_access_key', 
                's3_endpoint_url'
            ]
            for field in required_s3_fields:
                if not getattr(self, field):
                    raise ValueError(f"Production environment requires {field} to be set")

settings = Settings()
