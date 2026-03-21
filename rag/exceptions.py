"""Custom exceptions for the RAG system."""


class RAGError(Exception):
    """Base exception for all RAG system errors."""


class ConfigurationError(RAGError):
    """Raised when configuration loading or validation fails."""
    pass


class InsufficientEvidenceError(RAGError):
    """Raised when re-ranked context scores fall below the similarity threshold.

    This signals the generation layer to issue a refusal response rather than
    attempting to generate an answer from weak evidence.
    """

    def __init__(
        self,
        max_score: float,
        threshold: float,
        message: str | None = None,
    ) -> None:
        self.max_score = max_score
        self.threshold = threshold
        default = (
            f"Highest re-ranker score ({max_score:.4f}) is below the "
            f"similarity threshold ({threshold:.4f})."
        )
        super().__init__(message or default)


class IngestionError(RAGError):
    """Raised when PDF parsing or chunking fails irrecoverably."""