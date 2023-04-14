import base64
import datetime as dt
import json
from typing import Protocol

from jose import jws

from .config import AuthConfigDict
from .exceptions import AuthError
from .models import AccessTokenDict, IdTokenDict, PublicKey
from .validations import ValidateTokenPayload, validate_raw_token, validate_token_header, validate_token_signature


class MapToken(Protocol):
    def __call__(self, raw_token: str, payload: dict, header: dict) -> dict:
        pass


def parse_token(
    token: str | None,
    public_keys: list[PublicKey],
    validate_payload: ValidateTokenPayload,
    map_token: MapToken,
    config: AuthConfigDict,
) -> AccessTokenDict:

    validate_raw_token(token)

    payload = _parse_token_payload(token)
    validate_payload(payload, config=config)

    header = _parse_token_header(token)
    validate_token_header(header, config=config)

    key_id = header.get("kid")
    try:
        public_key = [key for key in public_keys if key["kid"] == key_id][0]
    except KeyError:
        raise AuthError("Invalid token key id")
    validate_token_signature(token, public_key)

    return map_token(token, payload, header)


def map_access_token(raw_token: str, payload: dict, header: dict) -> AccessTokenDict:
    return {
        "audiance": payload.get("client_id"),
        "expire_at": dt.datetime.fromtimestamp(payload.get("exp")),
        "issued_at": dt.datetime.fromtimestamp(payload.get("iat")),
        "issuer": payload.get("iss"),
        "jwt_id": payload.get("jti"),
        "raw": raw_token,
        "subject": payload.get("sub"),
    }


def map_id_token(raw_token: str, payload: dict, header: dict) -> IdTokenDict:
    return map_access_token(raw_token, payload, header) | {
        "email": payload.get("email"),
        "audiance": payload.get("aud"),
    }


def _parse_token_payload(token: str) -> dict:
    raw_payload = token.split(".")[1]
    try:
        payload = base64.b64decode(raw_payload + "=" * (4 - len(raw_payload) % 4))
    except Exception as e:
        raise AuthError("Invalid token payload") from e

    try:
        payload = json.loads(payload)
    except Exception as e:
        raise AuthError("Invalid token payload") from e

    return payload


def _parse_token_header(token: str) -> dict:
    try:
        header = jws.get_unverified_header(token)
    except Exception as e:
        raise AuthError("Invalid token header") from e

    return header
