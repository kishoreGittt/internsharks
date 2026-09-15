class AgentError(Exception):
    """
    Base exception for all agent-related errors.

    Attributes:
        message: Human-readable error message.
        code: Application-specific error code.
        retryable: Whether the operation can be retried.
        status_code: HTTP status code returned by the API.
    """

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        retryable: bool = False,
        status_code: int = 500,
    ):
        super().__init__(message)

        self.message = message
        self.code = code
        self.retryable = retryable
        self.status_code = status_code


class RetryableError(AgentError):
    """
    Exception for temporary failures that can be retried.

    Examples:
        - Temporary external API failure
        - Timeout
        - Service unavailable
    """

    def __init__(
        self,
        message: str,
        code: str = "RETRYABLE_ERROR",
        status_code: int = 503,
    ):
        super().__init__(
            message=message,
            code=code,
            retryable=True,
            status_code=status_code,
        )


class NonRetryableError(AgentError):
    """
    Exception for permanent failures that must not be retried.

    Examples:
        - Invalid request
        - Project not found
        - Invalid failure mode
    """

    def __init__(
        self,
        message: str,
        code: str = "NON_RETRYABLE_ERROR",
        status_code: int = 400,
    ):
        super().__init__(
            message=message,
            code=code,
            retryable=False,
            status_code=status_code,
        )