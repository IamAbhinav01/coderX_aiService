class BaseError(Exception):
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
