from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.vectors import EMBEDDING_DIMENSION, validate_embedding


def test_embedding_contract_accepts_exact_dimension() -> None:
    vector = validate_embedding([0.0] * EMBEDDING_DIMENSION)
    assert len(vector) == 1536


@pytest.mark.parametrize("size", [0, 1535, 1537])
def test_embedding_contract_rejects_other_dimensions(size: int) -> None:
    with pytest.raises(ValueError, match="exactly 1536"):
        validate_embedding([0.0] * size)

