class AgentError(Exception):
    def __init__(self, message, code="AGENT_ERROR", retryable=False, status_code=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable
        self.status_code = status_code

class RetryableError(AgentError):
    def __init__(self, message, code="TEMPORARY_FAILURE", status_code=503):
        super().__init__(message, code, True, status_code)

class NonRetryableError(AgentError):
    def __init__(self, message, code="INVALID_REQUEST", status_code=400):
        super().__init__(message, code, False, status_code)

class ToolTimeoutError(RetryableError):
    def __init__(self, message="Tool timed out"):
        super().__init__(message, "TOOL_TIMEOUT", 504)
