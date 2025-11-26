# Singapore Secondary School Cut-Off Points Scraper

A Python web scraper that collects secondary school cut-off point data along with addresses from sgschooling.com.

## Features

- ✅ Scrapes ~140 secondary schools with cut-off point data
- ✅ Includes historical data (2023, 2024, 2025)
- ✅ Extracts school addresses and town locations
- ✅ Filters out affiliated school entries
- ✅ Excludes special schools without cut-off points
- ✅ Automatic retry logic for failed requests
- ✅ Rate limiting (2-second delays) to be respectful
- ✅ Exports to CSV format

## Data Collected

- School Name
- Town
- Address
- Cut-off points for IP, PG3, PG2, PG1 (2023, 2024, 2025)
- School detail URL
- Scrape timestamp

## Installation

### 1. Set up virtual environment

```bash
cd /Users/ekchinhui/projects/posting
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the scraper

```bash
python scraper.py
```

The script will:
1. Fetch the main page with all schools
2. Visit each school's detail page (with 2-second delays)
3. Extract address and historical cut-off data
4. Export everything to `data/schools.csv`

**Estimated runtime:** ~7-8 minutes for all ~140 schools

## Configuration

You can customize settings in `.env`:

```env
REQUEST_DELAY=2.0      # Seconds between requests
MAX_RETRIES=3          # Max retry attempts per request
TIMEOUT=30             # Request timeout in seconds
OUTPUT_FILE=data/schools.csv  # Output file path
```

## Output Format

CSV file with columns:
- School Name, Town, Address
- 2025_IP, 2025_PG3, 2025_PG2, 2025_PG1
- 2024_IP, 2024_PG3, 2024_PG2, 2024_PG1
- 2023_IP, 2023_PG3, 2023_PG2, 2023_PG1
- Detail URL, Scrape Timestamp

## Project Structure

```
/Users/ekchinhui/projects/posting/
├── config.py                 # Configuration settings
├── scraper.py               # Main entry point
├── models/school.py         # School data model
├── parsers/
│   ├── main_page_parser.py  # Parse main table
│   └── detail_page_parser.py # Parse school details
├── utils/
│   ├── http_client.py       # HTTP with retry logic
│   ├── rate_limiter.py      # Rate limiting
│   └── csv_writer.py        # CSV export
└── data/schools.csv         # Output file
```

## Notes

- The scraper respectfully adds 2-second delays between requests
- Automatic retry logic handles temporary network issues
- Schools without cut-off points are excluded
- Affiliated school entries are filtered out (main school only)

## Legal & Ethics

- Data is scraped from publicly accessible pages
- Educational/research use case
- Respectful rate limiting implemented
- No circumvention of access controls

## License

For personal and educational use.
