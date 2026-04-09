class BaseError(Exception):
    """
    Custom application exception that carries an HTTP status code alongside
    a human-readable message and an optional technical detail string.

    Mirrors the JS  BaseError class from errors/Base.err.js.

    Usage:
        raise BaseError(400, "topic must be a non-empty string")
        raise BaseError(502, "LLM returned invalid JSON", str(e))
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict:
        """Serialise the error to a JSON-safe dict for HTTP responses."""
        payload: dict = {
            "error": self.message,
            "status_code": self.status_code,
        }
        if self.detail:
            payload["detail"] = self.detail
        return payload
