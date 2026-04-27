from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "outputs"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
APP_ENV = os.getenv("APP_ENV", "development")

for folder in [DATA_RAW_DIR, DATA_PROCESSED_DIR, OUTPUT_DIR, OUTPUT_DIR / "logs", OUTPUT_DIR / "reports", OUTPUT_DIR / "demo_exports"]:
    folder.mkdir(parents=True, exist_ok=True)
