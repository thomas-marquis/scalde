import json
import logging
from urllib.parse import quote_plus

import requests

from .config import AuthConfigDict
from .exceptions import AuthError, RetryableAuthError
from .models import PublicKey


def fetch_tokens(code: str, config: AuthConfigDict) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["redirect_uri"],
    }
    try:
        url = config["url"]
        resp = requests.post(
            f"{url}/oauth2/token",
            data=data,
            auth=(config["google_client_id"], config["google_client_secret"]),
        )
        resp.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"{e}; query data={data}; response={resp.text}")
        try:
            error = resp.json()["error"]
            raise RetryableAuthError(f"Failed to fetch tokens: {error}")
        except (KeyError, TypeError, json.JSONDecodeError):
            pass
        raise AuthError("Failed to fetch tokens")

    return resp.json()


def fetch_public_keys(config: AuthConfigDict) -> list[PublicKey]:
    try:
        url = config["issuer"]
        resp = requests.get(f"{url}/.well-known/jwks.json")
        resp.raise_for_status()
    except requests.HTTPError as e:
        logging.error(e)
        raise AuthError("Failed to fetch public keys: http error")

    return resp.json()["keys"]


def send_logout(config: AuthConfigDict) -> None:
    try:
        client_id = quote_plus(config["google_client_id"])
        redirect_uri = quote_plus(config["redirect_uri"])
        url = config["url"]
        response = requests.get(f"{url}/logout?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code")
        response.raise_for_status()
    except Exception as e:
        logging.error(e)
        raise AuthError("Failed to send logout")
