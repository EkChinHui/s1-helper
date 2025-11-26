import csv
import os
from typing import List
from models.school import School


class CSVWriter:
    """Handle CSV export with proper formatting"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self._ensure_directory()

    def _ensure_directory(self):
        """Create output directory if it doesn't exist"""
        directory = os.path.dirname(self.output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def write(self, schools: List[School]):
        """Write schools to CSV file"""
        if not schools:
            raise ValueError("No schools to write")

        with open(self.output_path, "w", newline="", encoding="utf-8") as f:
            # Get fieldnames from first school
            fieldnames = list(schools[0].to_dict().keys())

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for school in schools:
                writer.writerow(school.to_dict())

        print(f"✓ Exported {len(schools)} schools to {self.output_path}")
