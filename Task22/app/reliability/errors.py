class AgentError(Exception):
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