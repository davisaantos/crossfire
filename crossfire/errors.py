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


class DateError(CrossfireError):
    def __init__(self, initial_date, final_date):
        message = (
            f"initial_date `{initial_date}` is greater than final_date "
            f"`{final_date}`"
        )
        super().__init__(message)
