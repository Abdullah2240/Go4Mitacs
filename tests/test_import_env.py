from pathlib import Path
import sys

import pytest


def test_database_importer_requires_only_supabase_db_url(monkeypatch, capsys) -> None:
    import importlib.util

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "import_supabase.py"
    spec = importlib.util.spec_from_file_location("import_supabase_under_test", script_path)
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://local-only")
    monkeypatch.setattr(sys, "argv", ["import_supabase.py", "--limit", "100"])
    with pytest.raises(SystemExit) as error:
        importer.main()
    assert error.value.code == 2
    assert "SUPABASE_DB_URL is not set" in capsys.readouterr().err
