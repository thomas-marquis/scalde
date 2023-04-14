from typing import TypedDict


class AuthConfigDict(TypedDict):
    aws_region: str
    cognito_user_pool_id: str
    cognito_google_client_id: str
    cognito_google_client_secret: str
    cognito_url: str
    cognito_issuer: str
    algorithm: str
    redirect_uri: str
