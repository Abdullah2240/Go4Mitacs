from dataclasses import dataclass
import os
from pathlib import Path

from .env import load_repo_dotenv


load_repo_dotenv()

ROOT = Path(__file__).resolve().parents[2]


def _rooted_path(name: str, default: Path) -> Path:
    value = Path(os.getenv(name, str(default)))
    return value if value.is_absolute() else ROOT / value


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    corpus_manifest_path: Path = _rooted_path("CORPUS_MANIFEST_PATH", ROOT / "matcher-data" / "globalink-fetch-manifest.json")
    normalized_projects_path: Path = _rooted_path("NORMALIZED_PROJECTS_PATH", ROOT / "matcher-data" / "globalink-projects-normalized.jsonl")


settings = Settings()
