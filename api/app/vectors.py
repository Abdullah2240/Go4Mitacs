"""Server-side contract for future embedding vectors."""

from collections.abc import Sequence
import math


EMBEDDING_DIMENSION = 1536


def validate_embedding(values: Sequence[float], *, dimension: int = EMBEDDING_DIMENSION) -> list[float]:
    """Return a normalized vector or fail before any provider/database call."""
    if isinstance(values, (str, bytes)):
        raise TypeError("embedding must be a numeric sequence")
    vector = list(values)
    if len(vector) != dimension:
        raise ValueError(f"embedding dimension must be exactly {dimension}, got {len(vector)}")
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in vector):
        raise ValueError("embedding values must be finite numbers")
    return [float(value) for value in vector]

