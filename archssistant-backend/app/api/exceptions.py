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