"""Repository-local environment loading for server and CLI entry points."""

from pathlib import Path

from dotenv import load_dotenv


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load_repo_dotenv(repository_root: Path = REPOSITORY_ROOT) -> Path:
    """Load the repository .env without overriding explicitly exported values."""
    env_path = repository_root / ".env"
    load_dotenv(dotenv_path=env_path, override=False)
    return env_path

