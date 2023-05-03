import datetime as dt
from typing import TypedDict


class PublicKey(TypedDict):
    alg: str
    e: str
    kid: str
    kty: str
    n: str
    use: str


class TokenDict(TypedDict):
    raw: str


class AccessTokenDict(TokenDict):
    expire_at: dt.datetime
    audiance: str
    issuer: str
    issued_at: dt.datetime
    jwt_id: str
    subject: str


class IdTokenDict(AccessTokenDict):
    email: str


class TokensDict(TypedDict):
    access_token: AccessTokenDict
    id_token: AccessTokenDict
    refresh_token: TokenDict
