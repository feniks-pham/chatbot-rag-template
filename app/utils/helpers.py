import logging
from datetime import datetime
import os
import re

def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = f"{log_dir}/chatbot_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def format_chat_history(history):
    """Format chat history for display"""
    formatted = []
    for msg in history:
        formatted.append(f"{msg['role']}: {msg['content']}")
    return "\n".join(formatted)

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    try:
        import uuid
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False

def clean_markdown(text: str) -> str:
    # Delete inline code (`code`)
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Delete bold & italic (**bold**, *italic*, __, _)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Delete header markdown (#, ##, etc.)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Delete quote (>)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Delete list bullet
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # Delete code block ``` ```
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Delete space
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

