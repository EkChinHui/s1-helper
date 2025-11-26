# Singapore Secondary School Finder

An interactive web application to help students and parents find suitable Singapore secondary schools based on Achievement Level (AL) scores and location proximity.

[![Deploy to GitHub Pages](https://github.com/EkChinHui/s1-helper/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)](https://github.com/EkChinHui/s1-helper/actions)

## Features

### Smart AL Score Filtering

- **Automatic Posting Group Detection**: Enter your AL score and the app automatically determines your eligible posting groups based on MOE's official mappings:

  | AL Score | Eligible Posting Groups |
  |----------|------------------------|
  | 4-20     | PG3, IP |
  | 21-22    | PG2, PG3 |
  | 23-24    | PG2 |
  | 25       | PG1, PG2 |
  | 26-30    | PG1 |

- **Dynamic COP Display**: School cards only show Cut-Off Points for your eligible posting groups
- **Adjustable Range**: Set both minimum and maximum cut-off points to find schools that match your preferences
- **Historical Data Toggle**: Option to include schools based on historical maximum COP (2023-2025)

### Location-Based Search

- **Town Selection**: Choose from 29 Singapore towns/planning areas including:
  - Ang Mo Kio, Bedok, Bishan, Bukit Batok, Bukit Merah, Bukit Panjang, Bukit Timah
  - Central, Choa Chu Kang, Clementi, Geylang, Hougang, Jurong East, Jurong West
  - Kallang, Marine Parade, Novena, Pasir Ris, Punggol, Queenstown, Sembawang
  - Seng Kang, Serangoon, Tampines, **Tengah**, Toa Payoh, Woodlands, Yishun
- **Postal Code Lookup**: Enter your 6-digit postal code for precise location matching
- **Distance Filtering**: Find schools within a customizable radius (1-50 km)
- **Sort by Distance**: Sort results by nearest schools first when location is set
- **Automatic Geocoding**: Uses OneMap API for accurate Singapore addresses

### Interactive Map

- **Visual School Locations**: See all matching schools on an interactive map
- **Your Location Marker**: Clearly marked user location with custom icon
- **Distance Radius**: Visual circle showing your search radius
- **School Tooltips**: Hover over markers to see school names
- **Detailed Popups**: Click markers for school details and COP information
- **OneMap Integration**: Uses official Singapore government mapping service

### School Information Cards

Each school card displays:
- School name and full address
- Town/planning area
- Distance from your location (when location is set)
- **COP History Table**: 3-year historical cut-off points (2023-2025) for your eligible posting groups only

## Live Demo

Visit the live application: **[https://ekchinhhui.github.io/s1-helper/](https://ekchinhhui.github.io/s1-helper/)**

## Technology Stack

- **Frontend Framework**: React 19
- **Build Tool**: Vite 7
- **Mapping**:
  - Leaflet 1.9.4 (open-source mapping library)
  - React-Leaflet 5.0 (React components for Leaflet)
  - OneMap API (Singapore government mapping service)
- **Geolocation**:
  - GeoLib (distance calculations)
  - OneMap Geocoding API (postal code lookup)
- **Data Processing**: CSV parsing
- **Styling**: CSS3 with custom styles
- **Hosting**: GitHub Pages

## Prerequisites

- Node.js 20.19+ or 22.12+ and npm
- Modern web browser with JavaScript enabled
- Internet connection (for map tiles and geocoding API)

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/EkChinHui/s1-helper.git
cd s1-helper/school-finder
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

The optimized production build will be in the `dist/` folder.

### 5. Preview Production Build

```bash
npm run preview
```

## Data Format

The application expects a CSV file at `public/schools.csv` with the following columns:

```csv
School Name,Town,Address,2025_IP,2025_PG3,2025_PG2,2025_PG1,2024_IP,2024_PG3,2024_PG2,2024_PG1,2023_IP,2023_PG3,2023_PG2,2023_PG1,Detail URL,Scrape Timestamp,Latitude,Longitude
```

### Column Descriptions

| Column | Description | Example |
|--------|-------------|---------|
| `School Name` | Official school name | Raffles Institution |
| `Town` | Planning area/town | Bishan |
| `Address` | Full postal address | 1 Raffles Institution Lane Singapore 575954 |
| `2025_IP` | 2025 IP cut-off | 6 |
| `2025_PG1/2/3` | 2025 Posting Group cut-offs | 14 |
| `2024_*` / `2023_*` | Historical cut-offs | Same format |
| `Detail URL` | School info link | https://sgschooling.com/... |
| `Latitude` | School latitude | 1.3404 |
| `Longitude` | School longitude | 103.8481 |

### Score Format Examples

- **IP Scores**: `6`, `7M` (single/double digit, optionally with M for Mother Tongue affiliation)
- **PG Scores**: `14`, `22` (COP values - the upper bound of the AL range)
- **No Programme**: `-` or `--` (school doesn't offer this stream)

## Obtaining School Data

### Option 1: Use the Scraper (Recommended for Fresh Data)

The parent repository includes a Python web scraper:

```bash
# From the repository root
cd ..
pip install -r requirements.txt
python scraper.py
```

This will:
- Scrape ~140 Singapore secondary schools
- Extract cut-off points for all programmes (IP, PG1, PG2, PG3)
- Include 2023, 2024, and 2025 data
- Get school addresses and coordinates
- Output to `school-finder/public/schools.csv`

**Note**: The scraper extracts the upper bound (COP) from AL range data (e.g., "12 - 16" becomes "16").

### Option 2: Manual Data Entry

You can create your own CSV file based on data from:
- Ministry of Education (MOE) website
- School websites
- Education portals

### Option 3: Use Sample Data

The repository includes sample data for testing purposes in `public/schools.csv`.

## Deployment to GitHub Pages

### Automatic Deployment (Recommended)

The repository includes a GitHub Actions workflow that automatically deploys to GitHub Pages when you push to the main branch.

1. **Enable GitHub Pages**:
   - Go to your repository settings
   - Navigate to Pages
   - Source: Select "GitHub Actions"

2. **Push to Main Branch**:
   ```bash
   git add .
   git commit -m "Deploy school finder"
   git push origin main
   ```

3. **Wait for Deployment**:
   - Check the Actions tab for deployment progress
   - Once complete, visit: `https://[username].github.io/s1-helper/`

### Manual Deployment

If you prefer manual deployment:

```bash
cd school-finder
npm run build
cd ..

# Deploy the dist folder to gh-pages branch
npx gh-pages -d dist
```

## Configuration

### Changing Repository Name

If you fork this repository with a different name, update `vite.config.js`:

```javascript
export default defineConfig({
  base: '/your-repo-name/',  // Change this
  // ...
})
```

### Customizing Map Settings

Edit `src/App.jsx` to customize:

```javascript
// Default map zoom level
zoom={11}

// Default distance filter (km)
const [maxDistance, setMaxDistance] = useState(50);

// Map tile provider (currently OneMap)
url="https://www.onemap.gov.sg/maps/tiles/Default/{z}/{x}/{y}.png"
```

### Adding More Towns

Update the `TOWN_COORDS` object in `src/App.jsx`:

```javascript
const TOWN_COORDS = {
  'Your Town': { lat: 1.xxxx, lng: 103.xxxx },
  // ...
};
```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Internet Explorer: Not supported

## Privacy & Data

- **No User Data Collection**: This app runs entirely in your browser
- **No Cookies**: No tracking or analytics
- **External APIs**:
  - OneMap API for geocoding (postal code to coordinates)
  - OneMap tiles for map display
- **Data Source**: School data is scraped from public websites

## Known Issues & Limitations

1. **Geocoding Limits**: OneMap API has rate limits. If you make too many postal code lookups quickly, you may get errors.
2. **Browser Caching**: Map tiles are cached by your browser. Use Ctrl+Shift+R to force refresh if maps don't load.
3. **Mobile Performance**: Large datasets may be slower on older mobile devices.
4. **Scraper Reliability**: The web scraper may break if the source website changes structure.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with details and screenshots
2. **Suggest Features**: Describe new features you'd like to see
3. **Submit PRs**: Fork, make changes, and submit a pull request
4. **Update Data**: Help keep school data current

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/s1-helper.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
npm run dev

# Commit with clear messages
git commit -m "Add: your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## License

This project is for educational purposes. School data is publicly available information.

- Code: MIT License
- Data: Sourced from public websites (MOE, education portals)
- Maps: OneMap (Singapore Land Authority)

## Acknowledgments

- **OneMap**: Singapore Land Authority for mapping services
- **Ministry of Education (MOE)**: Official education data and posting group definitions
- **Leaflet**: Open-source mapping library
- **React + Vite**: Modern web development tools

## Support

- **Issues**: [GitHub Issues](https://github.com/EkChinHui/s1-helper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EkChinHui/s1-helper/discussions)

## Related Resources

- [MOE Secondary School Posting](https://www.moe.gov.sg/secondary/s1-posting)
- [MOE Full Subject-Based Banding](https://www.moe.gov.sg/microsites/psle-fsbb/full-subject-based-banding/secondary-school-posting.html)
- [OneMap API Documentation](https://www.onemap.gov.sg/docs/)
- [Singapore School Information](https://www.moe.gov.sg/schoolfinder)

---

*Last Updated: November 2025*
