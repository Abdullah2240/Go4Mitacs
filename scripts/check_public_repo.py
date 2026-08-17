"""Fail if staged files contain likely secrets or private material.

With no commits and no staged files this exits cleanly, making it safe to run
before the first commit. It only inspects the index, never file contents that
are merely present in the working tree.
"""

from pathlib import Path
import re
import subprocess
import sys


PRIVATE_PATH = re.compile(
    r"(^|/)(\.env(?:\.|$)|.*\.(?:pem|key|p12|crt|secret|token|pdf|sqlite|sqlite3|db)$|.*(?:certificate|lor|recommendation|application[-_ ]?record|private|gri[ _-]?docs).*)",
    re.IGNORECASE,
)
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(?:SUPABASE_SERVICE_ROLE_KEY|SUPABASE_DB_URL|DATABASE_URL|OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*=\s*['\"]?(?!<|your_|placeholder|changeme|from-dotenv|local-only|postgresql://local|env\()[^\s'\"]{12,}"),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,})\b"),
    re.compile(r"(?i)\b(?:service_role|anon)\s*[:=]\s*[A-Za-z0-9._-]{20,}\b"),
]


PUBLIC_SOURCE_DIRS = ("docs/", "matcher-docs/", "scripts/", "tests/", "api/migrations/", "supabase/migrations/", "supabase/rollback/")


def is_public_source_path(path: str) -> bool:
    return path == ".env.example" or path.startswith(PUBLIC_SOURCE_DIRS)


def staged_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def scan(paths: list[str]) -> list[str]:
    findings: list[str] = []
    for raw_path in paths:
        normalized = raw_path.replace("\\", "/")
        if PRIVATE_PATH.search(normalized) and not is_public_source_path(normalized):
            findings.append(f"private path: {raw_path}")
            continue
        staged = subprocess.run(
            ["git", "show", f":{raw_path}"],
            check=True,
            capture_output=True,
        ).stdout
        try:
            content = staged.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                findings.append(f"likely secret in staged file: {raw_path}")
                break
    return findings


def main() -> int:
    paths = staged_paths()
    if not paths:
        print("public repo check passed: no staged files")
        return 0
    findings = scan(paths)
    if findings:
        print("public repo check failed:")
        print("\n".join(f"- {finding}" for finding in findings))
        return 1
    print(f"public repo check passed: {len(paths)} staged files scanned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
