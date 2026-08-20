# app/spotify/exceptions.py
# Exceções customizadas para erros da Spotify API


class SpotifyAPIError(Exception):
    """Erro genérico da Spotify API."""

    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(SpotifyAPIError):
    """Rate limit excedido (HTTP 429)."""

    def __init__(self, message: str = "Rate limit excedido", retry_after: int = 0):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class TokenExpiredError(SpotifyAPIError):
    """Access token expirado (HTTP 401)."""

    def __init__(self, message: str = "Access token expirado"):
        super().__init__(message, status_code=401)


class TokenRevokedError(SpotifyAPIError):
    """Token revogado ou inválido."""

    def __init__(self, message: str = "Token revogado ou inválido"):
        super().__init__(message, status_code=401)


class InsufficientScopeError(SpotifyAPIError):
    """Scope insuficiente para a operação (HTTP 403)."""

    def __init__(self, message: str = "Scope insuficiente", required_scope: str | None = None):
        super().__init__(message, status_code=403)
        self.required_scope = required_scope


class NotFoundError(SpotifyAPIError):
    """Recurso não encontrado (HTTP 404)."""

    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status_code=404)


class ServerError(SpotifyAPIError):
    """Erro do servidor Spotify (HTTP 5xx)."""

    def __init__(self, message: str = "Erro interno do servidor Spotify", status_code: int = 500):
        super().__init__(message, status_code=status_code)
