import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for the scraper"""

    # URLs
    BASE_URL = "https://sgschooling.com"
    MAIN_PAGE_URL = f"{BASE_URL}/secondary/cop/all"

    # Rate Limiting
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))  # seconds
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))

    # Output
    OUTPUT_FILE = os.getenv("OUTPUT_FILE", "data/schools.csv")

    # Headers
    USER_AGENT = "Mozilla/5.0 (Educational Research Bot)"
