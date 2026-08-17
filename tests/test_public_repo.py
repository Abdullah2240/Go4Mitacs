from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_public_repo import PRIVATE_PATH, SECRET_PATTERNS


def test_private_paths_are_detected() -> None:
    assert PRIVATE_PATH.search("candidate/certificates/transcript.pdf")
    assert PRIVATE_PATH.search("2026 Mitacs GRI docs (good seniors)/notes.md")


def test_secret_patterns_are_detected() -> None:
    assert any(pattern.search("OPENAI_API_KEY=sk-" + "x" * 24) for pattern in SECRET_PATTERNS)

