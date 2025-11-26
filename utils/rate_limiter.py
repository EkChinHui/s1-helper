import time
from config import Config


class RateLimiter:
    """Rate limiter to add delays between requests"""

    def __init__(self, delay=Config.REQUEST_DELAY):
        self.delay = delay
        self.last_request_time = 0

    def wait(self):
        """Wait appropriate time before next request"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()
