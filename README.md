# Singapore Secondary School Cut-Off Points Scraper & Finder

A Python web scraper that collects secondary school cut-off point data from sgschooling.com, plus a React-based school finder application.

## Features

### Scraper
- Scrapes ~140 secondary schools with cut-off point data
- Includes historical data (2023, 2024, 2025)
- Extracts school addresses and town locations
- Separates affiliated vs non-affiliated cut-off points
- Separates HCL (Higher Chinese Language) grades (D/M/P) from numeric scores
- Detects school gender type (boys/girls/co-ed)
- Preview mode: scrapes 15 schools first, then prompts for confirmation
- Automatic retry logic for failed requests
- Rate limiting (2-second delays) to be respectful
- Exports to CSV format

### School Finder (React App)
- Filter schools by AL score based on eligible posting groups
- Filter by school type (boys/girls/co-ed/all)
- Filter by distance from your location (town or postal code)
- Support for affiliated school cut-off points
- Historical maximum cut-off option (2023-2025)
- Interactive map view with school markers
- Sort by name or distance

## Data Collected

- School Name
- Gender (boys/girls/mixed)
- Town
- Address
- Latitude/Longitude coordinates
- Cut-off points for IP, PG3, PG2, PG1 (2023, 2024, 2025)
- Affiliated cut-off points (IP_Aff, PG3_Aff, PG2_Aff, PG1_Aff)
- HCL grade columns (e.g., 2025_IP_HCL)
- School detail URL
- Scrape timestamp

## Installation

### Scraper

```bash
# Install dependencies using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

### School Finder

```bash
cd school-finder
npm install
```

## Usage

### Run the scraper

```bash
uv run python scraper.py
```

The script will:
1. Fetch the main page with all schools
2. Scrape 15 schools as a preview
3. Prompt for confirmation to continue
4. Visit each school's detail page (with 2-second delays)
5. Extract address, historical cut-off data, and affiliated cut-offs
6. Export everything to `data/schools.csv`

### Run the School Finder

```bash
cd school-finder
npm run dev
```

### Inject coordinates into CSV

If you have a raw CSV without coordinates:

```bash
uv run python inject_coordinates.py
```

This uses cached coordinates from `data/school_coordinates.json`.

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
- School Name, Gender, Town, Address
- 2025_IP, 2025_IP_HCL, 2025_IP_Aff, 2025_IP_Aff_HCL
- 2025_PG3, 2025_PG2, 2025_PG1
- 2025_PG3_Aff, 2025_PG3_Aff_HCL, 2025_PG2_Aff, 2025_PG2_Aff_HCL, 2025_PG1_Aff, 2025_PG1_Aff_HCL
- (Same pattern for 2024 and 2023)
- Detail URL, Scrape Timestamp

## Project Structure

```
s1-helper/
├── config.py                 # Configuration settings
├── scraper.py               # Main entry point
├── inject_coordinates.py    # Coordinate injection script
├── models/school.py         # School data model
├── parsers/
│   ├── main_page_parser.py  # Parse main table
│   └── detail_page_parser.py # Parse school details
├── utils/
│   ├── http_client.py       # HTTP with retry logic
│   ├── rate_limiter.py      # Rate limiting
│   └── csv_writer.py        # CSV export
├── data/
│   ├── schools.csv          # Output file
│   └── school_coordinates.json # Cached coordinates
└── school-finder/           # React application
    ├── src/App.jsx          # Main app component
    └── public/schools.csv   # CSV for frontend
```

## Notes

- The scraper respectfully adds 2-second delays between requests
- Automatic retry logic handles temporary network issues
- Schools without cut-off points are excluded
- Affiliated cut-offs are extracted from detail pages where available
- HCL grades (D=Distinction, M=Merit, P=Pass) are stored separately for sorting

## Legal & Ethics

- Data is scraped from publicly accessible pages
- Educational/research use case
- Respectful rate limiting implemented
- No circumvention of access controls

## License

For personal and educational use.
