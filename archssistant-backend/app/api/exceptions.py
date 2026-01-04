"""Custom exceptions for the API Gateway layer.

This module defines domain-specific exceptions that are used throughout
the API layer for error handling and HTTP status code mapping.
"""


class GatewayError(Exception):
    """
    Exception that unifies the error handling of the gateway, allowing
    to specify the HTTP status code and error message in a clear and consistent way.
    
    Attributes:
        status_code (int)   : HTTP status code associated with the error
        detail (str)        : Descriptive error message
    """
    
    def __init__(self, status_code: int, detail: str):
        self.status_code    = status_code
        self.detail         = detail
        super().__init__(detail)


class ApiKeyError(Exception):
    """
    Configuration/authentication error related to the LLM API key.
    
    Used to distinguish credential failures (e.g. absence of DEEPSEEK_API_KEY
    or 401 authentication) from network/server errors. The HTTP API translates this to 401.
    """
    pass