class AuthError(Exception):
    pass


class RetryableAuthError(AuthError):
    pass


class AuthValidationError(Exception):
    pass


class TokenExpired(Exception):
    pass
