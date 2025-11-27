from bs4 import BeautifulSoup
from typing import Tuple, Optional, Dict


class DetailPageParser:
    """Parse individual school detail pages for address and historical cut-off data"""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "lxml")

    def parse(
        self,
    ) -> Tuple[Optional[str], Optional[str], Dict[str, Dict[str, Optional[str]]]]:
        """
        Extract town, address, and historical cut-off points

        Returns:
            (town, address, historical_data)
            where historical_data = {
                '2024': {'ip': ..., 'pg3': ..., 'pg2': ..., 'pg1': ...},
                '2023': {'ip': ..., 'pg3': ..., 'pg2': ..., 'pg1': ...}
            }
        """
        town = self._extract_field("Town")
        address = self._extract_field("Address")
        historical_data = self._extract_historical_cutoffs()

        return town, address, historical_data

    def _extract_field(self, field_name: str) -> Optional[str]:
        """Extract a specific field from School Info section"""
        # Strategy 1: Look for table with School Info header
        tables = self.soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th", "cell"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    if label.lower() == field_name.lower():
                        return cells[1].get_text(strip=True)

        return None

    def _extract_historical_cutoffs(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Extract historical cut-off points from PSLE AL Range History table

        The HTML structure has rows where:
        - Year cell contains "2025↳ Affiliated" (year + affiliated marker combined)
        - Data cells contain concatenated values like "5 - 910 - 22" (main + affiliated ranges)

        Returns dict with years as keys, each containing ip/pg3/pg2/pg1 values
        and affiliated values (ip_aff/pg3_aff/pg2_aff/pg1_aff)
        """
        from models.school import School
        import re

        historical_data = {"2025": {}, "2024": {}, "2023": {}}

        # Find the historical table (look for "PSLE AL Range History" heading or "Year" column)
        tables = self.soup.find_all("table")

        for table in tables:
            # Check if this is the historical cut-off table
            headers = table.find_all(["th", "columnheader"])
            header_text = [h.get_text(strip=True) for h in headers]

            # Look for table with Year, IP, PG3, PG2, PG1 columns
            if "Year" in header_text and "IP" in header_text:
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                else:
                    rows = table.find_all("tr")[1:]  # Skip header

                for row in rows:
                    cells = row.find_all(["td", "cell"])
                    if len(cells) >= 5:
                        year_cell = cells[0].get_text(strip=True)

                        # Extract year from cell (e.g., "2025↳ Affiliated" -> "2025")
                        year_match = re.match(r'^(202[345])', year_cell)
                        if not year_match:
                            continue
                        year = year_match.group(1)

                        # Check if this row has affiliated data
                        has_affiliated = "↳" in year_cell or "Affiliated" in year_cell

                        # Get raw cell values
                        ip_raw = cells[1].get_text(strip=True)
                        pg3_raw = cells[2].get_text(strip=True)
                        pg2_raw = cells[3].get_text(strip=True)
                        pg1_raw = cells[4].get_text(strip=True)

                        # Parse main (non-affiliated) values
                        ip_val, ip_hcl = self._parse_main_value(ip_raw)
                        pg3_val, _ = self._parse_main_value(pg3_raw)
                        pg2_val, _ = self._parse_main_value(pg2_raw)
                        pg1_val, _ = self._parse_main_value(pg1_raw)

                        historical_data[year] = {
                            "ip": ip_val,
                            "ip_hcl": ip_hcl,
                            "pg3": pg3_val,
                            "pg2": pg2_val,
                            "pg1": pg1_val,
                        }

                        # Parse affiliated values if present
                        if has_affiliated:
                            ip_aff, ip_aff_hcl = self._parse_affiliated_value(ip_raw)
                            pg3_aff, pg3_aff_hcl = self._parse_affiliated_value(pg3_raw)
                            pg2_aff, pg2_aff_hcl = self._parse_affiliated_value(pg2_raw)
                            pg1_aff, pg1_aff_hcl = self._parse_affiliated_value(pg1_raw)

                            historical_data[year]["ip_aff"] = ip_aff
                            historical_data[year]["ip_aff_hcl"] = ip_aff_hcl
                            historical_data[year]["pg3_aff"] = pg3_aff
                            historical_data[year]["pg3_aff_hcl"] = pg3_aff_hcl
                            historical_data[year]["pg2_aff"] = pg2_aff
                            historical_data[year]["pg2_aff_hcl"] = pg2_aff_hcl
                            historical_data[year]["pg1_aff"] = pg1_aff
                            historical_data[year]["pg1_aff_hcl"] = pg1_aff_hcl

                break  # Found the table, no need to continue

        return historical_data

    def _parse_main_value(self, raw: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse the main (non-affiliated) value from a cell.

        Formats:
        - "5 - 910 - 22" -> main range 5-9, aff range 10-22
        - "5 - 9M8M- 12" -> main range 5-9M, aff range 8M-12 (with HCL grades)
        - "6M- 8M" -> simple range 6M-8M (no affiliated)

        Returns the upper bound of the main range with HCL grade if present.
        """
        import re
        from models.school import School

        if not raw or raw.strip() in ["-", "--", ""]:
            return (None, None)

        # Normalize separators: replace "- " with " - " for consistent splitting
        normalized = re.sub(r'(?<!\s)-\s', ' - ', raw.strip())

        # Split by " - "
        parts = normalized.split(' - ')

        if len(parts) >= 3:
            # Format: main_min - combined - aff_max (possibly more parts)
            main_min = parts[0]
            combined = parts[1]  # Contains main_max + aff_min concatenated

            # Extract numeric values (strip HCL grades for comparison)
            main_min_num = re.match(r'^(\d+)', main_min)
            main_min_val = int(main_min_num.group(1)) if main_min_num else 0

            # Try different split points for combined portion
            # Combined could be "910" or "9M8M" or "9M8" etc.
            for split in range(1, len(combined)):
                main_max_str = combined[:split]
                aff_min_str = combined[split:]

                # Extract numeric parts
                main_max_match = re.match(r'^(\d+)([DMP])?', main_max_str, re.IGNORECASE)
                aff_min_match = re.match(r'^(\d+)', aff_min_str)

                if main_max_match and aff_min_match:
                    main_max_val = int(main_max_match.group(1))
                    aff_min_val = int(aff_min_match.group(1))

                    # Validate: main_min <= main_max
                    if main_min_val <= main_max_val:
                        score = main_max_match.group(1)
                        hcl = main_max_match.group(2).upper() if main_max_match.group(2) else None
                        return (score, hcl)

            # Fallback: try to extract from combined
            match = re.match(r'^(\d+)([DMP])?', combined, re.IGNORECASE)
            if match:
                return (match.group(1), match.group(2).upper() if match.group(2) else None)

        # If only 2 parts, it's a simple range "X - Y"
        if len(parts) == 2:
            match = re.match(r'^(\d+)([DMP])?', parts[1], re.IGNORECASE)
            if match:
                return (match.group(1), match.group(2).upper() if match.group(2) else None)

        # Try School's clean_cutoff_value as fallback
        return School.clean_cutoff_value(raw)

    def _parse_affiliated_value(self, raw: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse the affiliated value from a cell.

        Formats:
        - "5 - 910 - 22" -> aff range 10-22, return 22
        - "5 - 9M8M- 12" -> aff range 8M-12, return 12

        Returns the upper bound of the affiliated range with HCL grade if present.
        """
        import re

        if not raw or raw.strip() in ["-", "--", ""]:
            return (None, None)

        # Normalize separators: replace "- " with " - " for consistent splitting
        normalized = re.sub(r'(?<!\s)-\s', ' - ', raw.strip())

        # Split by " - "
        parts = normalized.split(' - ')

        if len(parts) >= 3:
            # Format: main_min - combined - aff_max
            main_min = parts[0]
            combined = parts[1]
            aff_max = parts[-1]  # Last part is affiliated max

            # Extract numeric value from aff_max
            match = re.match(r'^(\d+)([DMP])?', aff_max, re.IGNORECASE)
            if match:
                return (match.group(1), match.group(2).upper() if match.group(2) else None)

        # No affiliated value in simple format (only 2 parts)
        return (None, None)
