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

        Returns dict with years as keys, each containing ip/pg3/pg2/pg1 values
        """
        from models.school import School

        historical_data = {"2024": {}, "2023": {}}

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
                        year = cells[0].get_text(strip=True)

                        # Only extract 2024 and 2023 data
                        if year in ["2024", "2023"]:
                            ip_val = School.clean_cutoff_value(
                                cells[1].get_text(strip=True)
                            )
                            pg3_val = School.clean_cutoff_value(
                                cells[2].get_text(strip=True)
                            )
                            pg2_val = School.clean_cutoff_value(
                                cells[3].get_text(strip=True)
                            )
                            pg1_val = School.clean_cutoff_value(
                                cells[4].get_text(strip=True)
                            )

                            historical_data[year] = {
                                "ip": ip_val,
                                "pg3": pg3_val,
                                "pg2": pg2_val,
                                "pg1": pg1_val,
                            }

                break  # Found the table, no need to continue

        return historical_data
