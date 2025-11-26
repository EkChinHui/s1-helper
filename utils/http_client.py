import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config


class HTTPClient:
    """HTTP client with automatic retry logic"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})

    @retry(
        stop=stop_after_attempt(Config.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def get(self, url):
        """Fetch URL with automatic retry on failure"""
        response = self.session.get(url, timeout=Config.TIMEOUT)
        response.raise_for_status()
        return response

    def close(self):
        """Close the session"""
        self.session.close()
