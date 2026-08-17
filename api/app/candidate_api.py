"""Archived cloud candidate API; not registered in local-only mode."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from .auth import get_current_user_id
from .candidate_ingestion import validate_candidate_payload
from .db import connect


router = APIRouter(prefix="/api/v1/candidate", tags=["candidate"])

RESOURCE_FIELDS = {
    "facts": ["fact_type", "fact_text", "source_type", "source_ref", "confidence", "privacy_classification", "verified_at"],
    "skills": ["skill_name", "proficiency", "source_type", "source_ref", "confidence", "privacy_classification"],
    "experience": ["organization", "role_title", "description", "started_on", "ended_on", "source_type", "source_ref", "confidence", "privacy_classification"],
    "projects": ["title", "description", "role", "started_on", "ended_on", "source_type", "source_ref", "confidence", "privacy_classification"],
    "certificates": ["name", "issuer", "issued_on", "expires_on", "credential_ref", "source_type", "source_ref", "confidence", "privacy_classification"],
    "research": ["title", "venue", "abstract", "role", "published_on", "source_type", "source_ref", "confidence", "privacy_classification"],
    "documents": ["storage_bucket", "storage_path", "source_type", "source_ref", "content_hash", "original_filename", "mime_type", "size_bytes", "privacy_classification"],
}
TABLES = {name: f"candidate_{name if name != 'documents' else 'documents'}" for name in RESOURCE_FIELDS}


def _safe_payload(payload: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    # owner_id/profile_id are intentionally not accepted from the client.
    return {field: payload[field] for field in fields if field in payload}


def _ensure_profile(cursor, owner_id: str) -> str:
    cursor.execute(
        """
        INSERT INTO candidate_profiles (owner_id)
        VALUES (%s)
        ON CONFLICT (owner_id) DO UPDATE SET updated_at = now()
        RETURNING id
        """,
        (owner_id,),
    )
    return str(cursor.fetchone()[0])


def _error() -> HTTPException:
    return HTTPException(status_code=400, detail="candidate data request could not be completed")


@router.get("/profile")
def get_profile(owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, owner_id, display_name, summary, privacy_classification, created_at, updated_at FROM candidate_profiles WHERE owner_id = %s",
                (owner_id,),
            )
            row = cursor.fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="candidate database unavailable") from None
    if row is None:
        raise HTTPException(status_code=404, detail="candidate profile not found")
    return dict(zip(("id", "owner_id", "display_name", "summary", "privacy_classification", "created_at", "updated_at"), row))


@router.put("/profile")
def upsert_profile(payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    allowed = _safe_payload(payload, ["display_name", "summary", "privacy_classification"])
    columns = ["owner_id", *allowed]
    values = [owner_id, *allowed.values()]
    assignments = ", ".join(f"{column} = EXCLUDED.{column}" for column in allowed)
    conflict_assignments = assignments or "updated_at = now()"
    placeholders = ", ".join(["%s"] * len(values))
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO candidate_profiles ({', '.join(columns)}) VALUES ({placeholders})
                ON CONFLICT (owner_id) DO UPDATE SET {conflict_assignments}
                RETURNING id, owner_id, display_name, summary, privacy_classification, created_at, updated_at
                """,
                values,
            )
            row = cursor.fetchone()
        return dict(zip(("id", "owner_id", "display_name", "summary", "privacy_classification", "created_at", "updated_at"), row))
    except Exception:
        raise _error() from None


@router.post("/import")
def import_candidate_evidence(payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, int]:
    """Import structured facts without accepting an owner identifier from the client."""
    try:
        records = validate_candidate_payload(payload)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="invalid candidate evidence payload") from None
    if not records:
        return {"facts_imported": 0}
    try:
        with connect() as connection, connection.cursor() as cursor:
            profile_id = _ensure_profile(cursor, owner_id)
            for record in records:
                fields = {
                    "fact_type": record.get("fact_type", "evidence"),
                    "fact_text": record["fact_text"],
                    "source_type": record["source_type"],
                    "source_ref": record.get("source_ref"),
                    "confidence": record.get("confidence"),
                    "privacy_classification": record.get("privacy_classification", "private"),
                    "verified_at": record.get("verified_at"),
                }
                cursor.execute(
                    """
                    INSERT INTO candidate_facts
                        (profile_id, owner_id, fact_type, fact_text, source_type, source_ref,
                         confidence, privacy_classification, verified_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (profile_id, owner_id, *fields.values()),
                )
        return {"facts_imported": len(records)}
    except Exception:
        raise _error() from None


@router.get("/{resource}")
def list_candidate_records(
    resource: str,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    owner_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    if resource not in RESOURCE_FIELDS:
        raise HTTPException(status_code=404, detail="candidate resource not found")
    table = TABLES[resource]
    columns = ["id", "profile_id", "owner_id", *RESOURCE_FIELDS[resource], "created_at"]
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {', '.join(columns)} FROM {table} WHERE owner_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (owner_id, limit, offset),
            )
            rows = cursor.fetchall()
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE owner_id = %s", (owner_id,))
            total = cursor.fetchone()[0]
    except Exception:
        raise HTTPException(status_code=503, detail="candidate database unavailable") from None
    return {"items": [dict(zip(columns, row)) for row in rows], "total": total, "limit": limit, "offset": offset}


@router.post("/{resource}")
def create_candidate_record(resource: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    if resource not in RESOURCE_FIELDS:
        raise HTTPException(status_code=404, detail="candidate resource not found")
    allowed = _safe_payload(payload, RESOURCE_FIELDS[resource])
    if not allowed:
        raise HTTPException(status_code=400, detail="no candidate fields supplied")
    table = TABLES[resource]
    try:
        with connect() as connection, connection.cursor() as cursor:
            profile_id = _ensure_profile(cursor, owner_id)
            columns = ["profile_id", "owner_id", *allowed]
            values = [profile_id, owner_id, *allowed.values()]
            placeholders = ", ".join(["%s"] * len(values))
            cursor.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING id, profile_id, owner_id, {', '.join(allowed)}",
                values,
            )
            row = cursor.fetchone()
        return dict(zip(["id", "profile_id", "owner_id", *allowed], row))
    except Exception:
        raise _error() from None


@router.patch("/{resource}/{record_id}")
def update_candidate_record(resource: str, record_id: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    if resource not in RESOURCE_FIELDS:
        raise HTTPException(status_code=404, detail="candidate resource not found")
    allowed = _safe_payload(payload, RESOURCE_FIELDS[resource])
    if not allowed:
        raise HTTPException(status_code=400, detail="no candidate fields supplied")
    assignments = ", ".join(f"{field} = %s" for field in allowed)
    table = TABLES[resource]
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {table} SET {assignments}, updated_at = now() WHERE id = %s AND owner_id = %s RETURNING id, profile_id, owner_id",
                [*allowed.values(), record_id, owner_id],
            )
            row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="candidate record not found")
        return {"id": row[0], "profile_id": row[1], "owner_id": row[2], **allowed}
    except HTTPException:
        raise
    except Exception:
        raise _error() from None


@router.delete("/{resource}/{record_id}", status_code=204)
def delete_candidate_record(resource: str, record_id: str, owner_id: str = Depends(get_current_user_id)) -> None:
    if resource not in RESOURCE_FIELDS:
        raise HTTPException(status_code=404, detail="candidate resource not found")
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {TABLES[resource]} WHERE id = %s AND owner_id = %s", (record_id, owner_id))
            if cursor.rowcount != 1:
                raise HTTPException(status_code=404, detail="candidate record not found")
    except HTTPException:
        raise
    except Exception:
        raise _error() from None
