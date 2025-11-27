from bs4 import BeautifulSoup
from models.school import School
from typing import List
from config import Config


class MainPageParser:
    """Parse the main cut-off points table and filter schools"""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "lxml")

    def parse(self) -> List[School]:
        """Extract all schools from main table, filtering affiliated and special schools"""
        schools = []
        table = self._find_main_table()

        if not table:
            raise ValueError("Could not find main table")

        # Find all table rows, skip header
        tbody = table.find("tbody")
        if tbody:
            rows = tbody.find_all("tr")
        else:
            rows = table.find_all("tr")[1:]  # Skip header if no tbody

        for row in rows:
            school = self._parse_row(row)
            if school:
                # Filter: Skip affiliated schools (contains ↳ or "Affiliated")
                if "↳" in school.name or "Affiliated" in school.name:
                    continue

                # Filter: Skip schools with no cut-off data
                if not school.has_cutoff_data():
                    continue

                schools.append(school)

        return schools

    def _find_main_table(self):
        """Locate the main data table"""
        tables = self.soup.find_all("table")
        for table in tables:
            headers = table.find_all(["th", "columnheader"])
            header_text = [h.get_text(strip=True) for h in headers]
            if "School" in header_text and "IP" in header_text:
                return table
        return None

    def _parse_row(self, row) -> School:
        """Parse a single table row"""
        cells = row.find_all(["td", "cell"])
        if len(cells) < 6:  # Need rank, name, ip, pg3, pg2, pg1
            return None

        # Extract school name and link
        school_cell = cells[1]  # First cell is rank number
        school_link = school_cell.find("a", href=True)

        if not school_link:
            return None

        school_name = school_link.get_text(strip=True)

        # Extract detail URL
        detail_url = school_link.get("href", "")
        if detail_url and not detail_url.startswith("http"):
            detail_url = f"{Config.BASE_URL}{detail_url}"

        # Extract cut-off points (2025 data from main page)
        # clean_cutoff_value returns (score, hcl_grade) tuple
        ip_raw = cells[2].get_text(strip=True)
        pg3_raw = cells[3].get_text(strip=True)
        pg2_raw = cells[4].get_text(strip=True)
        pg1_raw = cells[5].get_text(strip=True)

        ip_cutoff, ip_hcl = School.clean_cutoff_value(ip_raw)
        pg3_cutoff, _ = School.clean_cutoff_value(pg3_raw)
        pg2_cutoff, _ = School.clean_cutoff_value(pg2_raw)
        pg1_cutoff, _ = School.clean_cutoff_value(pg1_raw)

        # Also extract affiliated values if present in combined format (e.g., "6M8M")
        ip_aff, ip_aff_hcl = School.clean_cutoff_value_affiliated(ip_raw)
        pg3_aff, pg3_aff_hcl = School.clean_cutoff_value_affiliated(pg3_raw)
        pg2_aff, pg2_aff_hcl = School.clean_cutoff_value_affiliated(pg2_raw)
        pg1_aff, pg1_aff_hcl = School.clean_cutoff_value_affiliated(pg1_raw)

        return School(
            name=school_name,
            detail_url=detail_url,
            cutoff_2025_ip=ip_cutoff,
            cutoff_2025_ip_hcl=ip_hcl,
            cutoff_2025_pg3=pg3_cutoff,
            cutoff_2025_pg2=pg2_cutoff,
            cutoff_2025_pg1=pg1_cutoff,
            cutoff_2025_pg3_aff=pg3_aff,
            cutoff_2025_pg3_aff_hcl=pg3_aff_hcl,
            cutoff_2025_pg2_aff=pg2_aff,
            cutoff_2025_pg2_aff_hcl=pg2_aff_hcl,
            cutoff_2025_pg1_aff=pg1_aff,
            cutoff_2025_pg1_aff_hcl=pg1_aff_hcl,
        )
