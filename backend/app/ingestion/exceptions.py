"""Domain-specific exceptions for AgriShield AI data ingestion."""

from typing import Any, Dict, List, Optional


class IngestionError(Exception):
    """Base exception for all ingestion-related errors."""

    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider_name = provider_name
        self.details = details or {}

    def __str__(self) -> str:
        prefix = f"[{self.provider_name}] " if self.provider_name else ""
        return f"{prefix}{self.message}"


class ProviderConnectionError(IngestionError):
    """Raised when an external data provider or telemetry endpoint is unreachable or times out."""


class ProviderAuthenticationError(IngestionError):
    """Raised when authentication credentials (API key, OAuth token, client cert) are missing or invalid."""


class ProviderRateLimitError(IngestionError):
    """Raised when provider rate limits or quota thresholds are exceeded."""

    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        retry_after_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, provider_name, details)
        self.retry_after_seconds = retry_after_seconds


class ProviderAccessVerificationError(IngestionError):
    """Raised when pre-flight connectivity or authorization check fails for an external provider."""


class DataExtractionError(IngestionError):
    """Raised when raw data retrieval succeeds but payload extraction or parsing fails."""


class SchemaNormalizationError(IngestionError):
    """Raised when raw extracted data cannot be normalized or validated into the target Pydantic schema."""

    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        raw_payload: Optional[Any] = None,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, provider_name, details)
        self.raw_payload = raw_payload
        self.validation_errors = validation_errors or []

