#!/usr/bin/env python3
"""
Scrape higher mother tongue languages offered by each school from MOE SchoolFinder.
"""

import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.moe.gov.sg/schoolfinder"

LANGUAGE_FILTERS = {
    "Higher Chinese Language": "Higher%20Chinese%20Language",
    "Higher Tamil Language": "Higher%20Tamil%20Language",
    "Higher Malay Language": "Higher%20Malay%20Language",
}


def build_url(language_filter: str) -> str:
    """Build the MOE SchoolFinder URL with the specified language filter."""
    return (
        f"{BASE_URL}?journey=Secondary%20school&q=*"
        f"&fq=school_journey_ss%3A%22Secondary%20school%22"
        f"&fq=subjects_offered_ss%3A(%22{language_filter}%22)"
        f"&sort=slug_s%20asc"
    )


def extract_schools_from_page(page) -> list[str]:
    """Extract school names from the current page."""
    schools = page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a[href*="schooldetail"]').forEach(link => {
                const nameEl = link.querySelector('p');
                if (nameEl) {
                    const name = nameEl.textContent.trim();
                    if (name && !name.includes('Add school')) {
                        results.push(name);
                    }
                }
            });
            return results;
        }
    """)
    return schools


def scrape_language(page, language_name: str, language_filter: str) -> list[str]:
    """Scrape all schools offering a specific higher mother tongue language."""
    url = build_url(language_filter)
    print(f"\nScraping {language_name}...")
    page.goto(url)

    # Wait for the page to load
    page.wait_for_selector('a[href*="schooldetail"]', timeout=15000)
    time.sleep(2)

    # Get total count
    count_text = page.locator('text=/Showing \\d+ Secondary schools/').first.inner_text()
    total_count = int(count_text.split()[1])
    print(f"  Found {total_count} schools")

    # Calculate expected pages (20 schools per page)
    expected_pages = (total_count + 19) // 20

    all_schools = []
    page_num = 1

    while page_num <= expected_pages:
        # Extract schools from current page
        schools = extract_schools_from_page(page)
        all_schools.extend(schools)
        print(f"  Page {page_num}: collected {len(schools)} schools (total: {len(all_schools)})")

        if page_num >= expected_pages:
            break

        # Click next using JavaScript to avoid button detection issues
        try:
            # Use JavaScript to find and click the enabled next button
            # The buttons use class 'moe-pagination__btn dir--right' for next buttons
            clicked = page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button.moe-pagination__btn.dir--right');
                    for (const btn of buttons) {
                        if (!btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)

            if not clicked:
                print(f"  Could not find enabled next button, stopping at page {page_num}")
                break

            # Wait for new content to load
            time.sleep(2)
            page.wait_for_selector('a[href*="schooldetail"]', timeout=10000)

        except Exception as e:
            print(f"  Error navigating: {e}")
            break

        page_num += 1

    # Remove duplicates while preserving order
    unique_schools = list(dict.fromkeys(all_schools))
    print(f"  Total unique schools: {len(unique_schools)}")

    return unique_schools


def main():
    """Main function to scrape all higher mother tongue languages."""
    print("Starting MOE SchoolFinder scraper for Higher Mother Tongue Languages")

    result = {
        "higher_chinese_language": [],
        "higher_tamil_language": [],
        "higher_malay_language": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Scrape each language
        for language_name, language_filter in LANGUAGE_FILTERS.items():
            key = language_name.lower().replace(" ", "_")
            schools = scrape_language(page, language_name, language_filter)
            result[key] = schools

        browser.close()

    # Save to JSON file
    output_file = "data/higher_mother_tongue.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Data saved to {output_file}")
    print(f"  - Higher Chinese Language: {len(result['higher_chinese_language'])} schools")
    print(f"  - Higher Tamil Language: {len(result['higher_tamil_language'])} schools")
    print(f"  - Higher Malay Language: {len(result['higher_malay_language'])} schools")


if __name__ == "__main__":
    main()
