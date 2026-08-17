from pathlib import Path


WEB_ROOT = Path(__file__).resolve().parents[1] / "web"


def test_browser_bundle_uses_public_supabase_configuration_only() -> None:
    source_paths = list((WEB_ROOT / "app").rglob("*.ts*")) + list((WEB_ROOT / "lib").rglob("*.ts*"))
    source = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)
    assert "SUPABASE_DB_URL" not in source
    assert "SUPABASE_SERVICE_ROLE_KEY" not in source
    assert "service_role" not in source
    assert "NEXT_PUBLIC_SUPABASE_URL" not in source
    assert "NEXT_PUBLIC_SUPABASE_ANON_KEY" not in source
    assert "createClient" not in source


def test_minimal_authenticated_mvp_flows_are_present() -> None:
    source = (WEB_ROOT / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Enable cloud sync" not in source
    assert "sessionStorage" in (WEB_ROOT / "lib" / "localMode.ts").read_text(encoding="utf-8")
    assert "signInWithPassword" not in source
    assert "/api/v1/projects" in source
    assert "/api/v1/local/matches" in source
