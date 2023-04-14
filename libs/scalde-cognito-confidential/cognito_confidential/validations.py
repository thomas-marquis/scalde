import datetime as dt
from typing import Protocol

from jose import jwk
from jose.utils import base64url_decode

from .config import AuthConfigDict
from .exceptions import AuthValidationError, TokenExpired
from .models import PublicKey


class ValidateTokenPayload(Protocol):
    def __call__(self, payload: dict, config: AuthConfigDict) -> None:
        pass


def validate_raw_token(token: str) -> None:
    if not token:
        raise AuthValidationError("Token is empty")
    if (nb_parts := len(token.split("."))) != 3:
        raise AuthValidationError(f"Invalid token format: expected 3 parts, got {nb_parts}")


def validate_token_header(header: dict, config: AuthConfigDict) -> None:
    if header.get("alg") != config["algorithm"]:
        raise AuthValidationError("Invalid token algorythm")


def validate_token_signature(token: str, public_key: PublicKey) -> None:
    message, signature = token.rsplit(".", 1)

    key = jwk.construct(public_key)
    decoded_signature = base64url_decode(signature.encode())

    if not key.verify(message.encode(), decoded_signature):
        raise AuthValidationError("Invalid token signature")


def validate_access_token_payload(payload: dict, config: AuthConfigDict) -> None:
    # validate expiration date
    expiration = payload.get("exp")
    if not expiration:
        raise AuthValidationError("Token is missing expiration")
    if dt.datetime.fromtimestamp(expiration) < dt.datetime.now():
        raise TokenExpired("Token is expired")

    # validate issuer
    if payload.get("iss") != config["issuer"]:
        raise AuthValidationError("Invalid token issuer")

    # validate subject
    if not payload.get("sub"):
        raise AuthValidationError("Missing token subject")

    # validate audience or client id
    aud = payload.get("aud") or payload.get("client_id")
    if aud != config["google_client_id"]:
        raise AuthValidationError(f"Invalid token audience or client id '{aud}'")

    # validate issued at
    if not payload.get("iat"):
        raise AuthValidationError("Missing token issued at")
    if (actual_iat := dt.datetime.fromtimestamp(payload.get("iat"))) > (now_dt := dt.datetime.now()):
        raise AuthValidationError(f"Invalid token issued at: {actual_iat} earlier than now {now_dt}")

    # validate jwt id
    if not payload.get("jti"):
        raise AuthValidationError("Missing token jwt id")


def validate_id_token_payload(payload: dict, config: AuthConfigDict) -> None:
    validate_access_token_payload(payload, config=config)
