"""Archived cloud shortlist API; not registered in local-only mode."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from .auth import get_current_user_id
from .candidate_api import _ensure_profile
from .db import connect


router = APIRouter(prefix="/api/v1/candidate/shortlists", tags=["shortlists"])
CLASSIFICATIONS = {"ambitious", "strong-fit", "reliable", "confirmed"}


def _safe_shortlist_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: payload[key] for key in ("name", "description") if key in payload}


def _db_error() -> HTTPException:
    return HTTPException(status_code=400, detail="shortlist request could not be completed")


@router.post("")
def create_shortlist(payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    fields = _safe_shortlist_payload(payload)
    if not fields.get("name"):
        raise HTTPException(status_code=422, detail="shortlist name is required")
    try:
        with connect() as connection, connection.cursor() as cursor:
            profile_id = _ensure_profile(cursor, owner_id)
            cursor.execute(
                """
                INSERT INTO candidate_shortlists (profile_id, owner_id, name, description)
                VALUES (%s, %s, %s, %s)
                RETURNING id, profile_id, owner_id, name, description, created_at, updated_at
                """,
                (profile_id, owner_id, fields["name"], fields.get("description")),
            )
            row = cursor.fetchone()
        return dict(zip(("id", "profile_id", "owner_id", "name", "description", "created_at", "updated_at"), row))
    except Exception:
        raise _db_error() from None


@router.get("")
def list_shortlists(
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    owner_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    columns = ("id", "profile_id", "owner_id", "name", "description", "created_at", "updated_at")
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {', '.join(columns)} FROM candidate_shortlists WHERE owner_id = %s ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                (owner_id, limit, offset),
            )
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM candidate_shortlists WHERE owner_id = %s", (owner_id,))
            total = cursor.fetchone()[0]
        return {"items": [dict(zip(columns, row)) for row in rows], "total": total, "limit": limit, "offset": offset}
    except Exception:
        raise HTTPException(status_code=503, detail="shortlist database unavailable") from None


@router.patch("/{shortlist_id}")
def update_shortlist(shortlist_id: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    fields = _safe_shortlist_payload(payload)
    if not fields:
        raise HTTPException(status_code=422, detail="no shortlist fields supplied")
    assignments = ", ".join(f"{key} = %s" for key in fields)
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE candidate_shortlists SET {assignments}, updated_at = now() WHERE id = %s AND owner_id = %s RETURNING id, profile_id, owner_id, name, description, created_at, updated_at",
                [*fields.values(), shortlist_id, owner_id],
            )
            row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="shortlist not found")
        return dict(zip(("id", "profile_id", "owner_id", "name", "description", "created_at", "updated_at"), row))
    except HTTPException:
        raise
    except Exception:
        raise _db_error() from None


@router.delete("/{shortlist_id}", status_code=204)
def delete_shortlist(shortlist_id: str, owner_id: str = Depends(get_current_user_id)) -> None:
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("DELETE FROM candidate_shortlists WHERE id = %s AND owner_id = %s", (shortlist_id, owner_id))
            if cursor.rowcount != 1:
                raise HTTPException(status_code=404, detail="shortlist not found")
    except HTTPException:
        raise
    except Exception:
        raise _db_error() from None


@router.get("/{shortlist_id}/comparison")
def compare_shortlist(shortlist_id: str, owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.name, s.description, i.id, i.project_id, i.display_order,
                       i.classification, p.title, p.narrative_text, p.metadata, p.source_url
                FROM candidate_shortlists s
                LEFT JOIN candidate_shortlist_items i
                  ON i.shortlist_id = s.id AND i.owner_id = s.owner_id
                LEFT JOIN mitacs_projects p ON p.project_id = i.project_id
                WHERE s.id = %s AND s.owner_id = %s
                ORDER BY i.display_order NULLS LAST, i.created_at
                """,
                (shortlist_id, owner_id),
            )
            rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="shortlist not found")
        first = rows[0]
        items = [
            {
                "id": row[3], "project_id": row[4], "display_order": row[5],
                "classification": row[6], "title": row[7], "text": row[8],
                "metadata": row[9], "source_url": row[10],
            }
            for row in rows if row[3] is not None
        ]
        return {"id": first[0], "name": first[1], "description": first[2], "items": items}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="comparison database unavailable") from None


@router.post("/{shortlist_id}/items")
def add_shortlist_item(shortlist_id: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    project_id = payload.get("project_id")
    classification = payload.get("classification", "strong-fit")
    if not project_id or classification not in CLASSIFICATIONS:
        raise HTTPException(status_code=422, detail="project_id and valid classification are required")
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT profile_id FROM candidate_shortlists WHERE id = %s AND owner_id = %s", (shortlist_id, owner_id))
            shortlist = cursor.fetchone()
            if shortlist is None:
                raise HTTPException(status_code=404, detail="shortlist not found")
            cursor.execute("SELECT COALESCE(MAX(display_order), -1) + 1 FROM candidate_shortlist_items WHERE shortlist_id = %s AND owner_id = %s", (shortlist_id, owner_id))
            display_order = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO candidate_shortlist_items
                    (shortlist_id, profile_id, owner_id, project_id, display_order, classification)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, shortlist_id, project_id, display_order, classification
                """,
                (shortlist_id, shortlist[0], owner_id, project_id, display_order, classification),
            )
            row = cursor.fetchone()
        return dict(zip(("id", "shortlist_id", "project_id", "display_order", "classification"), row))
    except HTTPException:
        raise
    except Exception:
        raise _db_error() from None


@router.delete("/{shortlist_id}/items/{item_id}", status_code=204)
def remove_shortlist_item(shortlist_id: str, item_id: str, owner_id: str = Depends(get_current_user_id)) -> None:
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("DELETE FROM candidate_shortlist_items WHERE id = %s AND shortlist_id = %s AND owner_id = %s", (item_id, shortlist_id, owner_id))
            if cursor.rowcount != 1:
                raise HTTPException(status_code=404, detail="shortlist item not found")
    except HTTPException:
        raise
    except Exception:
        raise _db_error() from None


@router.patch("/{shortlist_id}/items/{item_id}")
def update_shortlist_item(shortlist_id: str, item_id: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    classification = payload.get("classification")
    if classification not in CLASSIFICATIONS:
        raise HTTPException(status_code=422, detail="valid classification is required")
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE candidate_shortlist_items SET classification = %s, updated_at = now() WHERE id = %s AND shortlist_id = %s AND owner_id = %s RETURNING id, shortlist_id, project_id, display_order, classification",
                (classification, item_id, shortlist_id, owner_id),
            )
            row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="shortlist item not found")
        return dict(zip(("id", "shortlist_id", "project_id", "display_order", "classification"), row))
    except HTTPException:
        raise
    except Exception:
        raise _db_error() from None


@router.patch("/{shortlist_id}/items/reorder")
def reorder_shortlist_items(shortlist_id: str, payload: dict[str, Any], owner_id: str = Depends(get_current_user_id)) -> dict[str, int]:
    project_ids = payload.get("project_ids")
    if not isinstance(project_ids, list) or len(project_ids) != len(set(project_ids)):
        raise HTTPException(status_code=422, detail="project_ids must be a unique ordered list")
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE candidate_shortlist_items SET display_order = display_order + 100000 WHERE shortlist_id = %s AND owner_id = %s", (shortlist_id, owner_id))
            for index, project_id in enumerate(project_ids):
                cursor.execute(
                    "UPDATE candidate_shortlist_items SET display_order = %s, updated_at = now() WHERE shortlist_id = %s AND owner_id = %s AND project_id = %s",
                    (index, shortlist_id, owner_id, project_id),
                )
        return {"reordered": len(project_ids)}
    except Exception:
        raise _db_error() from None
