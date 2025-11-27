#!/usr/bin/env python3
"""
Add higher mother tongue language columns to the schools CSV file.
"""

import csv
import json


def main():
    # Load higher mother tongue data
    with open("data/higher_mother_tongue.json", "r", encoding="utf-8") as f:
        hmt_data = json.load(f)

    hcl_schools = set(hmt_data["higher_chinese_language"])
    htl_schools = set(hmt_data["higher_tamil_language"])
    hml_schools = set(hmt_data["higher_malay_language"])

    print(f"Loaded HMT data:")
    print(f"  - Higher Chinese Language: {len(hcl_schools)} schools")
    print(f"  - Higher Tamil Language: {len(htl_schools)} schools")
    print(f"  - Higher Malay Language: {len(hml_schools)} schools")

    # Read existing CSV
    rows = []
    with open("data/coord.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"\nRead {len(rows)} schools from coord.csv")

    # Add new columns
    new_fieldnames = list(fieldnames) + ["HCL", "HTL", "HML"]

    # Update each row with HMT data
    hcl_count = 0
    htl_count = 0
    hml_count = 0

    for row in rows:
        school_name = row["School Name"]

        # Check each language
        has_hcl = school_name in hcl_schools
        has_htl = school_name in htl_schools
        has_hml = school_name in hml_schools

        row["HCL"] = "Y" if has_hcl else "-"
        row["HTL"] = "Y" if has_htl else "-"
        row["HML"] = "Y" if has_hml else "-"

        if has_hcl:
            hcl_count += 1
        if has_htl:
            htl_count += 1
        if has_hml:
            hml_count += 1

    print(f"\nMatched schools:")
    print(f"  - HCL: {hcl_count}/{len(hcl_schools)}")
    print(f"  - HTL: {htl_count}/{len(htl_schools)}")
    print(f"  - HML: {hml_count}/{len(hml_schools)}")

    # Write updated CSV
    with open("data/coord.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Updated coord.csv with HCL, HTL, HML columns")

    # Also update the school-finder public CSV
    with open("school-finder/public/schools.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Updated school-finder/public/schools.csv")


if __name__ == "__main__":
    main()
