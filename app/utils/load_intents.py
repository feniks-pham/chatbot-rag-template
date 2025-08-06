import yaml
import os

def get_project_root() -> str:
    """Trả về thư mục gốc của project"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_intents() -> dict:
    root = get_project_root()
    full_path = os.path.join(root, "templates", "intents.yaml")
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def load_prompt_template(file_path: str) -> str:
    root = get_project_root()
    full_path = os.path.join(root, "templates", file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()