class CrossfireError(Exception):
    pass


class RetryAfterError(CrossfireError):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        message = (
            "Got HTTP Status 429 Too Many Requests. "
            f"Retry after {self.retry_after} seconds"
        )
        super().__init__(message)
