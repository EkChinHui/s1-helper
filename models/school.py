from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime
import re


@dataclass
class School:
    """Represents a secondary school with all scraped data including historical cut-off points"""

    # Basic info
    name: str
    detail_url: str

    # Location (from detail page)
    town: Optional[str] = None
    address: Optional[str] = None

    # School type
    gender: Optional[str] = None  # 'boys', 'girls', or 'mixed'

    # 2025 cut-off points (from main page)
    cutoff_2025_ip: Optional[str] = None
    cutoff_2025_ip_hcl: Optional[str] = None
    cutoff_2025_pg3: Optional[str] = None
    cutoff_2025_pg2: Optional[str] = None
    cutoff_2025_pg1: Optional[str] = None
    # 2025 affiliated cut-off points
    cutoff_2025_ip_aff: Optional[str] = None
    cutoff_2025_ip_aff_hcl: Optional[str] = None
    cutoff_2025_pg3_aff: Optional[str] = None
    cutoff_2025_pg3_aff_hcl: Optional[str] = None
    cutoff_2025_pg2_aff: Optional[str] = None
    cutoff_2025_pg2_aff_hcl: Optional[str] = None
    cutoff_2025_pg1_aff: Optional[str] = None
    cutoff_2025_pg1_aff_hcl: Optional[str] = None

    # 2024 cut-off points (from detail page)
    cutoff_2024_ip: Optional[str] = None
    cutoff_2024_ip_hcl: Optional[str] = None
    cutoff_2024_pg3: Optional[str] = None
    cutoff_2024_pg2: Optional[str] = None
    cutoff_2024_pg1: Optional[str] = None
    # 2024 affiliated cut-off points
    cutoff_2024_ip_aff: Optional[str] = None
    cutoff_2024_ip_aff_hcl: Optional[str] = None
    cutoff_2024_pg3_aff: Optional[str] = None
    cutoff_2024_pg3_aff_hcl: Optional[str] = None
    cutoff_2024_pg2_aff: Optional[str] = None
    cutoff_2024_pg2_aff_hcl: Optional[str] = None
    cutoff_2024_pg1_aff: Optional[str] = None
    cutoff_2024_pg1_aff_hcl: Optional[str] = None

    # 2023 cut-off points (from detail page)
    cutoff_2023_ip: Optional[str] = None
    cutoff_2023_ip_hcl: Optional[str] = None
    cutoff_2023_pg3: Optional[str] = None
    cutoff_2023_pg2: Optional[str] = None
    cutoff_2023_pg1: Optional[str] = None
    # 2023 affiliated cut-off points
    cutoff_2023_ip_aff: Optional[str] = None
    cutoff_2023_ip_aff_hcl: Optional[str] = None
    cutoff_2023_pg3_aff: Optional[str] = None
    cutoff_2023_pg3_aff_hcl: Optional[str] = None
    cutoff_2023_pg2_aff: Optional[str] = None
    cutoff_2023_pg2_aff_hcl: Optional[str] = None
    cutoff_2023_pg1_aff: Optional[str] = None
    cutoff_2023_pg1_aff_hcl: Optional[str] = None

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

    def derive_gender(self) -> str:
        """Determine school gender type from school name"""
        name = self.name.lower()
        # Girls' schools - check for common patterns
        if ("girls" in name or
            "convent" in name or
            "canossian" in name or
            name.startswith("chij") or
            "cedar" in name or
            "crescent" in name or
            "nanyang" in name and "high" in name or
            "singapore chinese" in name):
            return "girls"
        # Boys' schools - check for common patterns
        if ("boys" in name or
            "st. joseph" in name or
            "st. andrew" in name or
            "st. patrick" in name or
            "st. gabriel" in name or
            "catholic high" in name or
            "hwa chong" in name or
            "raffles institution" in name or
            "anglo-chinese" in name or
            "maris stella" in name or
            "montfort" in name or
            "victoria" in name and "junior" not in name or  # Victoria School, not Victoria JC
            "beatty" in name):
            return "boys"
        return "mixed"

    def to_dict(self):
        """Convert to dictionary for CSV export"""
        return {
            "School Name": self.name,
            "Gender": self.gender or self.derive_gender(),
            "Town": self.town or "N/A",
            "Address": self.address or "N/A",
            # 2025 cutoffs
            "2025_IP": self.cutoff_2025_ip or "-",
            "2025_IP_HCL": self.cutoff_2025_ip_hcl or "-",
            "2025_IP_Aff": self.cutoff_2025_ip_aff or "-",
            "2025_IP_Aff_HCL": self.cutoff_2025_ip_aff_hcl or "-",
            "2025_PG3": self.cutoff_2025_pg3 or "-",
            "2025_PG2": self.cutoff_2025_pg2 or "-",
            "2025_PG1": self.cutoff_2025_pg1 or "-",
            "2025_PG3_Aff": self.cutoff_2025_pg3_aff or "-",
            "2025_PG3_Aff_HCL": self.cutoff_2025_pg3_aff_hcl or "-",
            "2025_PG2_Aff": self.cutoff_2025_pg2_aff or "-",
            "2025_PG2_Aff_HCL": self.cutoff_2025_pg2_aff_hcl or "-",
            "2025_PG1_Aff": self.cutoff_2025_pg1_aff or "-",
            "2025_PG1_Aff_HCL": self.cutoff_2025_pg1_aff_hcl or "-",
            # 2024 cutoffs
            "2024_IP": self.cutoff_2024_ip or "-",
            "2024_IP_HCL": self.cutoff_2024_ip_hcl or "-",
            "2024_IP_Aff": self.cutoff_2024_ip_aff or "-",
            "2024_IP_Aff_HCL": self.cutoff_2024_ip_aff_hcl or "-",
            "2024_PG3": self.cutoff_2024_pg3 or "-",
            "2024_PG2": self.cutoff_2024_pg2 or "-",
            "2024_PG1": self.cutoff_2024_pg1 or "-",
            "2024_PG3_Aff": self.cutoff_2024_pg3_aff or "-",
            "2024_PG3_Aff_HCL": self.cutoff_2024_pg3_aff_hcl or "-",
            "2024_PG2_Aff": self.cutoff_2024_pg2_aff or "-",
            "2024_PG2_Aff_HCL": self.cutoff_2024_pg2_aff_hcl or "-",
            "2024_PG1_Aff": self.cutoff_2024_pg1_aff or "-",
            "2024_PG1_Aff_HCL": self.cutoff_2024_pg1_aff_hcl or "-",
            # 2023 cutoffs
            "2023_IP": self.cutoff_2023_ip or "-",
            "2023_IP_HCL": self.cutoff_2023_ip_hcl or "-",
            "2023_IP_Aff": self.cutoff_2023_ip_aff or "-",
            "2023_IP_Aff_HCL": self.cutoff_2023_ip_aff_hcl or "-",
            "2023_PG3": self.cutoff_2023_pg3 or "-",
            "2023_PG2": self.cutoff_2023_pg2 or "-",
            "2023_PG1": self.cutoff_2023_pg1 or "-",
            "2023_PG3_Aff": self.cutoff_2023_pg3_aff or "-",
            "2023_PG3_Aff_HCL": self.cutoff_2023_pg3_aff_hcl or "-",
            "2023_PG2_Aff": self.cutoff_2023_pg2_aff or "-",
            "2023_PG2_Aff_HCL": self.cutoff_2023_pg2_aff_hcl or "-",
            "2023_PG1_Aff": self.cutoff_2023_pg1_aff or "-",
            "2023_PG1_Aff_HCL": self.cutoff_2023_pg1_aff_hcl or "-",
            "Detail URL": self.detail_url,
            "Scrape Timestamp": self.scrape_timestamp,
        }

    @staticmethod
    def clean_cutoff_value(value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Clean and validate cutoff point values, separating HCL grade suffix.

        Returns:
            (score, hcl_grade) tuple where:
            - score is the numeric cutoff (as string for consistency)
            - hcl_grade is D/M/P if present, None otherwise
        """
        if not value or value.strip() == "-" or value.strip() == "--":
            return (None, None)
        cleaned = value.strip()

        # Handle range values like "12 - 16" or "8 - 20" - extract upper bound (COP)
        if " - " in cleaned:
            parts = cleaned.split(" - ")
            if len(parts) == 2:
                cleaned = parts[1].strip()  # Use upper bound

        # Handle multiple values in one cell (e.g., "6M 8M" or "6M8M" for affiliated)
        # Take the first value for main school
        parts = cleaned.split()
        if parts:
            cleaned = parts[0]

        # Handle format like "7-" or "7M-" (score with optional HCL grade, dash indicates no affiliated)
        match = re.match(r'^(\d{1,2})([DMP])?-$', cleaned, re.IGNORECASE)
        if match:
            score = match.group(1)
            hcl_grade = match.group(2).upper() if match.group(2) else None
            return (score, hcl_grade)

        # Handle concatenated format with HCL grade like "6M8M" - extract first score+grade
        # Pattern: single/double digit number with D/M/P, followed by more digits
        match = re.match(r'^(\d{1,2})([DMP])(\d+)', cleaned, re.IGNORECASE)
        if match:
            score = match.group(1)
            hcl_grade = match.group(2).upper()
            return (score, hcl_grade)

        # Handle concatenated format without HCL grade like "713" (7+13) or "2125" (21+25)
        # For 3-digit values: split as 1+2 (e.g., "713" -> 7, 13)
        # For 4-digit values: split as 2+2 (e.g., "2125" -> 21, 25)
        if cleaned.isdigit():
            if len(cleaned) == 3:
                return (cleaned[0], None)  # First digit is non-affiliated score
            elif len(cleaned) == 4:
                return (cleaned[:2], None)  # First two digits are non-affiliated score

        # Handle simple format like "6M" or "7D" or plain "8"
        match = re.match(r'^(\d{1,2})([DMP])?$', cleaned, re.IGNORECASE)
        if match:
            score = match.group(1)
            hcl_grade = match.group(2).upper() if match.group(2) else None
            return (score, hcl_grade)

        # If no match, return as-is with no HCL grade
        return (cleaned if cleaned else None, None)

    @staticmethod
    def clean_cutoff_value_affiliated(value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract affiliated cutoff value from combined format like "6M8M" or "6M 8M" or "713".

        Returns:
            (score, hcl_grade) tuple for the affiliated (second) value
        """
        if not value or value.strip() == "-" or value.strip() == "--":
            return (None, None)
        cleaned = value.strip()

        # Handle range values - extract upper bound
        if " - " in cleaned:
            parts = cleaned.split(" - ")
            if len(parts) == 2:
                cleaned = parts[1].strip()

        # Handle space-separated format like "6M 8M"
        parts = cleaned.split()
        if len(parts) >= 2:
            cleaned = parts[1]  # Take second value for affiliated
            # Extract HCL grade from the affiliated value
            match = re.match(r'^(\d{1,2})([DMP])?$', cleaned, re.IGNORECASE)
            if match:
                score = match.group(1)
                hcl_grade = match.group(2).upper() if match.group(2) else None
                return (score, hcl_grade)
            return (cleaned, None)

        # Handle concatenated format with HCL grade like "6M8M" - extract second score+grade
        # Pattern: skip first number+grade, capture second number+optional grade
        match = re.match(r'^\d{1,2}[DMP](\d{1,2})([DMP])?$', cleaned, re.IGNORECASE)
        if match:
            score = match.group(1)
            hcl_grade = match.group(2).upper() if match.group(2) else None
            return (score, hcl_grade)

        # Handle concatenated format without HCL grade like "713" (7+13) or "2125" (21+25)
        # For 3-digit values: split as 1+2 (e.g., "713" -> 7, 13) - return 13
        # For 4-digit values: split as 2+2 (e.g., "2125" -> 21, 25) - return 25
        if cleaned.isdigit():
            if len(cleaned) == 3:
                return (cleaned[1:], None)  # Last two digits are affiliated score
            elif len(cleaned) == 4:
                return (cleaned[2:], None)  # Last two digits are affiliated score

        # No affiliated value found
        return (None, None)
