from pathlib import Path
import os
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.env import REPOSITORY_ROOT, load_repo_dotenv


def test_default_env_path_is_repository_root() -> None:
    assert load_repo_dotenv() == REPOSITORY_ROOT / ".env"


def test_dotenv_values_are_loaded(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SUPABASE_DB_URL=from-dotenv\nDATABASE_URL=local-db\n", encoding="utf-8")
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    load_repo_dotenv(tmp_path)
    assert os.environ["SUPABASE_DB_URL"] == "from-dotenv"
    assert os.environ["DATABASE_URL"] == "local-db"


def test_exported_environment_wins_over_dotenv(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SUPABASE_DB_URL=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("SUPABASE_DB_URL", "from-shell")
    load_repo_dotenv(tmp_path)
    assert os.environ["SUPABASE_DB_URL"] == "from-shell"


def test_importer_never_prints_database_url() -> None:
    secret = "postgresql://secret-user:secret-password@db.example.test/private"
    child_env = os.environ.copy()
    child_env["SUPABASE_DB_URL"] = secret
    result = subprocess.run(
        [sys.executable, "scripts/import_supabase.py", "--dry-run", "--limit", "100"],
        cwd=REPOSITORY_ROOT,
        env=child_env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert secret not in result.stdout
    assert secret not in result.stderr
    assert "secret-password" not in result.stdout + result.stderr

