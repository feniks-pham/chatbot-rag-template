import logging
import sys
import os
from datetime import datetime
from pythonjsonlogger import json

from app.config.settings import settings

# Tạo thư mục logs nếu chưa có
log_dir = os.path.expanduser(settings.log_dir)
os.makedirs(log_dir, exist_ok=True)

# Stream handler console
stream_handler = logging.StreamHandler(sys.stdout)
stream_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
)
stream_handler.setFormatter(stream_formatter)

# File handler JSON logs
current_date = datetime.now().strftime("%Y%m%d")
log_file = os.path.join(log_dir, f'chatbot_{current_date}.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
json_formatter = json.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s %(pathname)s',
    json_ensure_ascii=False
)
file_handler.setFormatter(json_formatter)

# Config root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[stream_handler, file_handler],
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("s3transfer").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module"""
    return logging.getLogger(name)

# Default logger
logger = get_logger(__name__)
logger.info(f"Logger initialized. Log file: {log_file}")
