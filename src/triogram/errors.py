class ApiError(RuntimeError):
    """
    API error occurred.
    """


class AuthError(ApiError):
    """
    Authentication failed.
    """
