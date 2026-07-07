from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    model: str
    ollama_host: str | None
    data_dir: Path


def load_settings() -> Settings:
    load_dotenv()  # Load environment variables from .env file if it exists
    model = os.getenv("OLLAMA_MODEL")
    if not model:
        raise ValueError("Environment variable 'OLLAMA_MODEL' is not set")
    ollama_host = os.getenv("OLLAMA_HOST", None)
    data_dir = Path(os.getenv("PAGENT_DATA_DIR", "~/.pagent")).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)  # Ensure the data directory exists
    return Settings(model=model, ollama_host=ollama_host, data_dir=data_dir)
