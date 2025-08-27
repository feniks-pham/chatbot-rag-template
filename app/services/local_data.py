import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from typing import List, Dict
from app.config.settings import settings
from app.utils.logger import get_logger
from langchain_text_splitters import MarkdownTextSplitter
from transformers import AutoTokenizer

logger = get_logger(__name__)

# ======= PDF helpers =======
def _safe_import(mod):
    try:
        return __import__(mod)
    except Exception:
        return None

pdfplumber = _safe_import("pdfplumber")
camelot = _safe_import("camelot")
tabula = _safe_import("tabula")

def _chunk_by_tokens(text: str, tokenizer, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Cắt chuỗi theo số token dùng HuggingFace tokenizer.
    """
    if not text:
        return []
    ids = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    if not ids:
        return []
    start = 0
    step = max(1, chunk_size - chunk_overlap)
    while start < len(ids):
        end = min(start + chunk_size, len(ids))
        sub_ids = ids[start:end]
        chunk = tokenizer.decode(sub_ids, skip_special_tokens=True).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(ids):
            break
        start += step
    return chunks

def _extract_pdf_text_by_page(pdf_path: str) -> List[Dict]:
    """
    Trả về [{"page": int, "text": str}]
    """
    if not pdfplumber:
        raise RuntimeError("Thiếu thư viện pdfplumber. Vui lòng cài: pip install pdfplumber")

    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            try:
                txt = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                txt = txt.strip()
                if txt:
                    out.append({"page": i, "text": txt})
            except Exception as e:
                logger.warning(f"[PDF] skip text on page {i} due to: {e}")
                continue
    return out

def _extract_pdf_tables(pdf_path: str) -> List[Dict]:
    """
    Trả về list dict:
      {
        "page": int|None,
        "csv": str,
        "rows": List[List[str]],
        "columns": List[str] | None
      }
    Ưu tiên Camelot -> Tabula -> pdfplumber
    """
    results: List[Dict] = []

    # 1) Camelot
    if camelot:
        try:
            for flavor in ("lattice", "stream"):
                try:
                    tables = camelot.read_pdf(pdf_path, flavor=flavor, pages="all")
                    for t in tables:
                        df = t.df
                        if df is not None and not df.empty:
                            # Chuẩn hóa về str để tránh None
                            df = df.astype(str)
                            rows = df.values.tolist()
                            columns = [str(c) for c in getattr(df, "columns", [])]
                            results.append({
                                "page": int(getattr(t, "page", None)) if getattr(t, "page", None) else None,
                                "csv": df.to_csv(index=False),
                                "rows": rows,
                                "columns": columns if columns else None
                            })
                except Exception:
                    continue
            if results:
                return results
        except Exception:
            pass

    # 2) Tabula
    if tabula:
        try:
            dfs = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
            for df in dfs or []:
                if df is not None and not df.empty:
                    df = df.astype(str)
                    rows = df.values.tolist()
                    columns = [str(c) for c in getattr(df, "columns", [])]
                    results.append({
                        "page": None,
                        "csv": df.to_csv(index=False),
                        "rows": rows,
                        "columns": columns if columns else None
                    })
            if results:
                return results
        except Exception:
            pass

    # 3) Fallback pdfplumber
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    try:
                        tables = page.extract_tables() or []
                        for tbl in tables:
                            rows = []
                            for row in tbl:
                                if row is None:
                                    continue
                                row = [("" if c is None else str(c).replace("\n", " ").strip()) for c in row]
                                rows.append(row)
                            if rows:
                                # CSV text đơn giản
                                csv_lines = []
                                for r in rows:
                                    csv_lines.append(",".join([str(x) for x in r]))
                                csv_text = "\n".join(csv_lines)
                                results.append({"page": i, "csv": csv_text, "rows": rows, "columns": None})
                    except Exception as e:
                        logger.warning(f"[PDF] skip tables on page {i} due to: {e}")
                        continue
        except Exception:
            pass

    return results
# ======= End PDF helpers =======

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
                splitter = MarkdownTextSplitter.from_huggingface_tokenizer(tokenizer=tokenizer, chunk_size=1000, chunk_overlap=200)
                data = splitter.split_text(md_data)
                logger.info(f"Successfully processed {len(data)} chunks from local file")
                return data
            
            elif file_type == ".md":
                with open(data_file, "r", encoding="utf-8") as f:
                    md_data = f.read()
                logger.info(f"Markdown file {data_file} loaded")

                tokenizer = AutoTokenizer.from_pretrained(
                    settings.embedding_model_name,
                    token=settings.hf_token,
                    trust_remote_code=True
                )
                # chunk theo token
                md_chunks = _chunk_by_tokens(md_data, tokenizer, chunk_size=1000, chunk_overlap=200)
                logger.info(f"Successfully processed {len(md_chunks)} chunks from markdown")
                return md_chunks

            elif file_type == ".pdf":
                # 1) Text theo trang
                text_pages = _extract_pdf_text_by_page(data_file)
                # 2) Bảng
                table_items = _extract_pdf_tables(data_file)

                # 3) Ghép sections
                sections: List[str] = []
                for item in text_pages:
                    p = item["page"]
                    sections.append(f"[PDF p.{p} - text]\n{item['text']}")

                for tb in table_items:
                    p = tb.get("page")
                    rows = tb.get("rows") or []
                    cols = tb.get("columns")
                    meta_obj = {
                        "page": p,
                        "n_rows": len(rows),
                        "n_cols": (len(rows[0]) if rows else 0),
                        "columns": cols  # có thể None nếu fallback
                    }
                    prefix = f"[PDF p.{p} - table]" if p else "[PDF - table]"
                    sections.append(
                        f"{prefix}\n"
                        f"[TABLE_META]{json.dumps(meta_obj, ensure_ascii=False)}\n"
                        f"{tb['csv']}"
                    )

                # 4) Chunk theo token
                tokenizer = AutoTokenizer.from_pretrained(
                    settings.embedding_model_name,
                    token=settings.hf_token,
                    trust_remote_code=True
                )
                pdf_chunks: List[str] = []
                for sec in sections:
                    pdf_chunks.extend(_chunk_by_tokens(sec, tokenizer, chunk_size=1000, chunk_overlap=200))

                logger.info(f"Successfully processed {len(pdf_chunks)} chunks from PDF")
                return pdf_chunks

            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        except FileNotFoundError:
            logger.error(f"Local data file not found: {data_file}")
            raise Exception(f"Local data file not found: {data_file}")
        except Exception as e:
            logger.error(f"Error loading Q&A data from local file: {str(e)}")
            raise Exception(f"Failed to Q&A load data from local file: {str(e)}")