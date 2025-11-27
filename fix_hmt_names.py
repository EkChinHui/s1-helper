#!/usr/bin/env python3
"""
Fix school names in higher_mother_tongue.json to match coord.csv naming convention.
"""

import csv
import json
from difflib import SequenceMatcher

# Read coord.csv school names
coord_schools = set()
with open("data/coord.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        coord_schools.add(row["School Name"])

print(f"Found {len(coord_schools)} schools in coord.csv")

# Read higher_mother_tongue.json
with open("data/higher_mother_tongue.json", "r", encoding="utf-8") as f:
    hmt_data = json.load(f)

# Build name mapping from MOE to coord.csv format
def normalize_name(name):
    """Normalize school name for comparison."""
    name = name.lower()
    # Remove common suffixes and variations
    replacements = [
        ("secondary school", ""),
        ("(secondary)", ""),
        (" secondary", ""),
        ("school", ""),
        ("'s", "s"),
        ("'", "'"),
        ("  ", " "),
    ]
    for old, new in replacements:
        name = name.replace(old, new)
    return name.strip()

def find_best_match(moe_name, coord_schools):
    """Find the best matching name in coord.csv."""
    moe_norm = normalize_name(moe_name)

    best_match = None
    best_score = 0

    for coord_name in coord_schools:
        coord_norm = normalize_name(coord_name)

        # Exact match after normalization
        if moe_norm == coord_norm:
            return coord_name

        # Check if one contains the other
        if moe_norm in coord_norm or coord_norm in moe_norm:
            score = SequenceMatcher(None, moe_norm, coord_norm).ratio()
            if score > best_score:
                best_score = score
                best_match = coord_name
        else:
            score = SequenceMatcher(None, moe_norm, coord_norm).ratio()
            if score > best_score and score > 0.6:
                best_score = score
                best_match = coord_name

    return best_match

# Create mapping
name_mapping = {}
unmatched = []

all_moe_names = set()
for lang in hmt_data:
    all_moe_names.update(hmt_data[lang])

print(f"\nMapping {len(all_moe_names)} unique MOE school names...")

for moe_name in sorted(all_moe_names):
    match = find_best_match(moe_name, coord_schools)
    if match:
        name_mapping[moe_name] = match
        if moe_name != match:
            print(f"  '{moe_name}' -> '{match}'")
    else:
        unmatched.append(moe_name)
        print(f"  WARNING: No match for '{moe_name}'")

print(f"\nMatched: {len(name_mapping)}, Unmatched: {len(unmatched)}")

# Apply mapping to the data
fixed_data = {}
for lang, schools in hmt_data.items():
    fixed_schools = []
    for school in schools:
        if school in name_mapping:
            fixed_schools.append(name_mapping[school])
        else:
            # Keep original if no match (will be flagged as unmatched)
            fixed_schools.append(school)
    # Remove duplicates and sort
    fixed_schools = sorted(set(fixed_schools))
    fixed_data[lang] = fixed_schools

# Add Nanyang Girls' High to higher_chinese_language
if "Nanyang Girls' High" not in fixed_data["higher_chinese_language"]:
    fixed_data["higher_chinese_language"].append("Nanyang Girls' High")
    fixed_data["higher_chinese_language"] = sorted(fixed_data["higher_chinese_language"])
    print("\nAdded 'Nanyang Girls' High' to higher_chinese_language")

# Save fixed data
with open("data/higher_mother_tongue.json", "w", encoding="utf-8") as f:
    json.dump(fixed_data, f, indent=2, ensure_ascii=False)

print(f"\n✓ Fixed data saved to data/higher_mother_tongue.json")
print(f"  - Higher Chinese Language: {len(fixed_data['higher_chinese_language'])} schools")
print(f"  - Higher Tamil Language: {len(fixed_data['higher_tamil_language'])} schools")
print(f"  - Higher Malay Language: {len(fixed_data['higher_malay_language'])} schools")

# Report schools in HMT but not in coord.csv
print("\n--- Schools in HMT data but NOT in coord.csv ---")
for lang, schools in fixed_data.items():
    for school in schools:
        if school not in coord_schools:
            print(f"  [{lang}] {school}")
