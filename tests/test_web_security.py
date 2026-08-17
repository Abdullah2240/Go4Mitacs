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


def test_browser_uses_same_origin_routes_without_deployment_api_env() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in (list((WEB_ROOT / "app").rglob("*.ts*")) + list((WEB_ROOT / "lib").rglob("*.ts*"))))
    assert "NEXT_PUBLIC_API_URL" not in source
    assert 'fetch("/api/local/matches' in source


def test_public_index_contains_no_raw_ingestion_fields() -> None:
    import json
    index = json.loads((WEB_ROOT / "data" / "mitacs-projects.public.json").read_text(encoding="utf-8"))
    assert index["count"] == 3359
    assert len(index["projects"]) == 3359
    assert "text" not in index["projects"][0]
    assert "metadata" not in index["projects"][0]


def test_minimal_authenticated_mvp_flows_are_present() -> None:
    source = (WEB_ROOT / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Enable cloud sync" not in source
    assert "sessionStorage" in (WEB_ROOT / "lib" / "localMode.ts").read_text(encoding="utf-8")
    assert "signInWithPassword" not in source
    assert "/api/v1/projects" in source
    assert "/api/v1/local/matches" in source
