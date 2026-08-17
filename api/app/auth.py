"""Archived Supabase Auth helper; not imported by the local-only product."""

import json
from urllib.request import Request, urlopen

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings


bearer = HTTPBearer(auto_error=False)


def _reject(detail: str = "authentication required") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def user_id_from_token(token: str) -> str:
    if not token or len(token) > 8192:
        raise _reject("invalid bearer token")
    if settings.supabase_jwt_secret:
        import jwt

        try:
            claims = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
        except jwt.PyJWTError:
            raise _reject("invalid bearer token") from None
        user_id = claims.get("sub")
        if not isinstance(user_id, str) or not user_id:
            raise _reject("invalid bearer token")
        return user_id
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(status_code=503, detail="authentication is not configured")
    request = Request(
        f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
        headers={"apikey": settings.supabase_anon_key, "Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        user_id = payload.get("id")
    except Exception:
        raise _reject("invalid bearer token") from None
    if not isinstance(user_id, str) or not user_id:
        raise _reject("invalid bearer token")
    return user_id


def get_current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _reject()
    return user_id_from_token(credentials.credentials)
