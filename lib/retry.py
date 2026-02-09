"""
Retry decorator with exponential backoff and jitter.

Usage:
    from lib.retry import retry_with_backoff

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_data():
        ...

    # With alert on exhaustion:
    @retry_with_backoff(max_retries=3, on_exhausted=lambda e: send_alert(f"API down: {e}"))
    def call_api():
        ...
"""
import functools
import random
import time
import logging

log = logging.getLogger("cortana.retry")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = (Exception,),
    on_exhausted=None,
):
    """Decorator: retry with exponential backoff + jitter.

    Args:
        max_retries: Number of retry attempts after the first failure.
        base_delay: Initial delay in seconds (doubled each retry).
        max_delay: Cap on delay between retries.
        retryable_exceptions: Tuple of exception types that trigger a retry.
        on_exhausted: Optional callback(exception) invoked when all retries fail.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exc = exc
                    if attempt == max_retries:
                        break
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.3)
                    wait = delay + jitter
                    log.warning(
                        "Retry %d/%d for %s after %.1fs: %s",
                        attempt + 1,
                        max_retries,
                        func.__name__,
                        wait,
                        exc,
                    )
                    time.sleep(wait)

            log.error(
                "All %d retries exhausted for %s: %s",
                max_retries,
                func.__name__,
                last_exc,
            )
            if on_exhausted:
                try:
                    on_exhausted(last_exc)
                except Exception as cb_err:
                    log.error("on_exhausted callback failed: %s", cb_err)
            raise last_exc

        return wrapper

    return decorator
