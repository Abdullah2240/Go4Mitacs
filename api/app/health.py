from typing import Any

from .config import settings


def readiness() -> dict[str, Any]:
    manifest_ok = settings.corpus_manifest_path.exists()
    projects_ok = settings.normalized_projects_path.exists()
    ready = manifest_ok and projects_ok
    return {
        "status": "ok" if ready else "degraded",
        "checks": {
            "manifest": "ok" if manifest_ok else "missing",
            "normalized_projects": "ok" if projects_ok else "missing",
        },
    }
