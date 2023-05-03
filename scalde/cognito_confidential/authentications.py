import datetime as dt
import logging
from urllib.parse import quote_plus

from .clients import fetch_public_keys, fetch_tokens, send_logout
from .config import AuthConfigDict
from .exceptions import AuthError
from .models import PublicKey, TokensDict
from .parsers import map_access_token, map_id_token, parse_token
from .stores import AuthStore
from .validations import validate_access_token_payload, validate_id_token_payload


def get_public_keys(config: AuthConfigDict, store: AuthStore | None = None) -> list[PublicKey]:
    if store and "public_keys" in store:
        print("public keys already fetched")
        return store.public_keys

    try:
        public_keys = fetch_public_keys(config=config)
    except Exception as e:
        logging.error(e)
        raise AuthError("Failed to fetch public keys")

    if not public_keys:
        raise AuthError("Failed to fetch public keys: empty response")

    if store:
        store.public_keys = public_keys

    return public_keys


def get_authorization_url(config: AuthConfigDict) -> str:
    redirect_uri = quote_plus(config["redirect_uri"])
    client_id = quote_plus(config["google_client_id"])
    url = config["url"]

    return f"{url}/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"


def get_tokens(
    code: str | None,
    config: AuthConfigDict,
    public_keys: list[PublicKey] | None = None,
    store: AuthStore | None = None,
) -> TokensDict:
    if not public_keys and not store:
        raise ValueError("Either public_keys or store must be provided")
    if not public_keys:
        public_keys = store.public_keys

    existing_access_token = store.access_token if store and "access_token" in store else None
    if existing_access_token and existing_access_token["expire_at"] > dt.datetime.now():
        logging.debug("tokens already exists in store and still valid")
        return {
            "access_token": existing_access_token,
            "id_token": store.id_token,
            "refresh_token": store.refresh_token,
        }

    if not code:
        return {}

    tokens_resp = fetch_tokens(code, config=config)

    access_token = parse_token(
        token=tokens_resp["access_token"],
        public_keys=public_keys,
        validate_payload=validate_access_token_payload,
        map_token=map_access_token,
        config=config,
    )

    id_token = parse_token(
        token=tokens_resp["id_token"],
        public_keys=public_keys,
        validate_payload=validate_id_token_payload,
        map_token=map_id_token,
        config=config,
    )

    refresh_token = {
        "raw": tokens_resp["refresh_token"],
    }

    if store:
        store.access_token = access_token
        store.id_token = id_token
        store.refresh_token = refresh_token

    return {
        "access_token": access_token,
        "id_token": id_token,
        "refresh_token": refresh_token,
    }


def refresh_tokens(config: AuthConfigDict) -> None:
    raise NotImplementedError("refresh_tokens not implemented yet")


def logout(config: AuthConfigDict, store: AuthStore | None = None) -> None:
    send_logout(config=config)
    if store:
        del store.access_token
        del store.id_token
        del store.refresh_token
