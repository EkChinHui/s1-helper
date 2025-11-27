#!/usr/bin/env python3
"""
Inject latitude and longitude coordinates into a schools CSV file
using pre-cached coordinate data.
"""

import csv
import json
import argparse
from pathlib import Path


def load_coordinates(coords_file: str) -> dict:
    """Load school coordinates from JSON file."""
    with open(coords_file, "r", encoding="utf-8") as f:
        return json.load(f)


def inject_coordinates(input_csv: str, output_csv: str, coords_file: str):
    """
    Read input CSV, add Latitude and Longitude columns, write to output CSV.

    Args:
        input_csv: Path to input CSV file (without coordinates)
        output_csv: Path to output CSV file (with coordinates)
        coords_file: Path to JSON file with school coordinates
    """
    coordinates = load_coordinates(coords_file)

    with open(input_csv, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames.copy()

        # Add Latitude and Longitude columns if not present
        if "Latitude" not in fieldnames:
            fieldnames.append("Latitude")
        if "Longitude" not in fieldnames:
            fieldnames.append("Longitude")

        rows = []
        matched = 0
        unmatched = []

        for row in reader:
            school_name = row.get("School Name", "")

            if school_name in coordinates:
                row["Latitude"] = coordinates[school_name]["latitude"]
                row["Longitude"] = coordinates[school_name]["longitude"]
                matched += 1
            else:
                row["Latitude"] = ""
                row["Longitude"] = ""
                unmatched.append(school_name)

            rows.append(row)

    with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {len(rows)} schools")
    print(f"  Matched: {matched}")
    print(f"  Unmatched: {len(unmatched)}")

    if unmatched:
        print("\nUnmatched schools:")
        for name in unmatched:
            print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Inject coordinates into schools CSV file"
    )
    parser.add_argument(
        "input_csv",
        help="Input CSV file path"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file path (default: overwrites input file)"
    )
    parser.add_argument(
        "-c", "--coords",
        default="data/school_coordinates.json",
        help="Path to coordinates JSON file (default: data/school_coordinates.json)"
    )

    args = parser.parse_args()

    output_csv = args.output if args.output else args.input_csv

    inject_coordinates(args.input_csv, output_csv, args.coords)
    print(f"\nOutput written to: {output_csv}")


if __name__ == "__main__":
    main()
