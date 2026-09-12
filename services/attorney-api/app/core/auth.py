from functools import lru_cache
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import get_settings
bearer=HTTPBearer()
@lru_cache
def jwks(): return jwt.PyJWKClient(get_settings().oidc_jwks_url)
def current_attorney(credentials: HTTPAuthorizationCredentials=Security(bearer)) -> dict:
    try:
        token=jwt.decode(credentials.credentials,jwks().get_signing_key_from_jwt(credentials.credentials).key,algorithms=["RS256"],issuer=get_settings().oidc_issuer_url,options={"verify_aud":False})
    except jwt.PyJWTError as exc: raise HTTPException(401,"Invalid access token") from exc
    roles=set(token.get("realm_access",{}).get("roles",[]))
    if not roles.intersection({"attorney","admin"}): raise HTTPException(403,"Attorney role required")
    return token