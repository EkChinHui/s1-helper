from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class School:
    """Represents a secondary school with all scraped data including historical cut-off points"""

    # Basic info
    name: str
    detail_url: str

    # Location (from detail page)
    town: Optional[str] = None
    address: Optional[str] = None

    # 2025 cut-off points (from main page)
    cutoff_2025_ip: Optional[str] = None
    cutoff_2025_pg3: Optional[str] = None
    cutoff_2025_pg2: Optional[str] = None
    cutoff_2025_pg1: Optional[str] = None

    # 2024 cut-off points (from detail page)
    cutoff_2024_ip: Optional[str] = None
    cutoff_2024_pg3: Optional[str] = None
    cutoff_2024_pg2: Optional[str] = None
    cutoff_2024_pg1: Optional[str] = None

    # 2023 cut-off points (from detail page)
    cutoff_2023_ip: Optional[str] = None
    cutoff_2023_pg3: Optional[str] = None
    cutoff_2023_pg2: Optional[str] = None
    cutoff_2023_pg1: Optional[str] = None

    # Metadata
    scrape_timestamp: Optional[str] = None

    def __post_init__(self):
        """Set timestamp if not provided"""
        if self.scrape_timestamp is None:
            self.scrape_timestamp = datetime.now().isoformat()

    def has_cutoff_data(self) -> bool:
        """Check if school has any cut-off point data"""
        return any(
            [
                self.cutoff_2025_ip,
                self.cutoff_2025_pg3,
                self.cutoff_2025_pg2,
                self.cutoff_2025_pg1,
            ]
        )

    def to_dict(self):
        """Convert to dictionary for CSV export"""
        return {
            "School Name": self.name,
            "Town": self.town or "N/A",
            "Address": self.address or "N/A",
            "2025_IP": self.cutoff_2025_ip or "-",
            "2025_PG3": self.cutoff_2025_pg3 or "-",
            "2025_PG2": self.cutoff_2025_pg2 or "-",
            "2025_PG1": self.cutoff_2025_pg1 or "-",
            "2024_IP": self.cutoff_2024_ip or "-",
            "2024_PG3": self.cutoff_2024_pg3 or "-",
            "2024_PG2": self.cutoff_2024_pg2 or "-",
            "2024_PG1": self.cutoff_2024_pg1 or "-",
            "2023_IP": self.cutoff_2023_ip or "-",
            "2023_PG3": self.cutoff_2023_pg3 or "-",
            "2023_PG2": self.cutoff_2023_pg2 or "-",
            "2023_PG1": self.cutoff_2023_pg1 or "-",
            "Detail URL": self.detail_url,
            "Scrape Timestamp": self.scrape_timestamp,
        }

    @staticmethod
    def clean_cutoff_value(value: str) -> Optional[str]:
        """Clean and validate cutoff point values"""
        if not value or value.strip() == "-":
            return None
        cleaned = value.strip()
        # Handle multiple values in one cell (e.g., "6M 8M" for affiliated)
        # Take the first value for main school
        parts = cleaned.split()
        if parts:
            return parts[0]
        return cleaned
