# 🏫 Singapore Secondary School Finder

An interactive web application to help students and parents find suitable Singapore secondary schools based on Achievement Level (AL) scores and location proximity.

[![Deploy to GitHub Pages](https://github.com/EkChinHui/s1-helper/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)](https://github.com/EkChinHui/s1-helper/actions)

## 🌟 Features

### Smart Filtering
- **AL Score Filtering**: Find schools you can get into based on your 2025 AL score
- **Multiple Streams**: Filter by Integrated Programme (IP), Phase 1 (PG1), Phase 2 (PG2), or Phase 3 (PG3)
- **Adjustable Range**: Set both minimum and maximum cut-off points to find schools that match your preferences
- **Historical Data**: Includes cut-off data from 2023, 2024, and 2025

### Location-Based Search
- **Town Selection**: Choose from 28+ Singapore towns/planning areas
- **Postal Code Lookup**: Enter your postal code for precise location matching
- **Distance Filtering**: Find schools within a customizable radius (1-50 km)
- **Automatic Geocoding**: Uses OneMap API for accurate Singapore addresses

### Interactive Map
- **Visual School Locations**: See all matching schools on an interactive map
- **Your Location Marker**: Clearly marked user location with custom icon
- **Distance Radius**: Visual circle showing your search radius
- **School Tooltips**: Hover over markers to see school names
- **Detailed Popups**: Click markers for school details, AL scores, and distances
- **OneMap Integration**: Uses official Singapore government mapping service

### School Information
- School name and full address
- Town/planning area
- Current and historical AL cut-off points
- Distance from your location
- Direct links to detailed school information

## 🚀 Live Demo

Visit the live application: **[https://ekchinhhui.github.io/s1-helper/](https://ekchinhhui.github.io/s1-helper/)**

## 📸 Screenshots

### Filter Interface
Filter schools by AL score and location with intuitive sliders and dropdowns.

### Map View
See all matching schools on an interactive map with distance indicators.

### School Cards
Browse detailed school information in a clean, card-based layout.

## 🛠️ Technology Stack

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

## 📋 Prerequisites

- Node.js 18+ and npm
- Modern web browser with JavaScript enabled
- Internet connection (for map tiles and geocoding API)

## 💻 Local Development

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

## 📊 Data Format

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
| `2025_IP` | 2025 IP cut-off | 4- |
| `2025_PG1/2/3` | 2025 Phase cut-offs | 9-13 |
| `2024_*` / `2023_*` | Historical cut-offs | Same format |
| `Detail URL` | School info link | https://sgschooling.com/... |
| `Latitude` | School latitude | 1.3404 |
| `Longitude` | School longitude | 103.8481 |

### Score Format Examples

- **IP Scores**: `4-`, `6-`, `7M-` (single digit, optionally with M for Mother Tongue)
- **PG Scores**: `9-13`, `2125` (ranges)
- **No Programme**: `--` or `-` (school doesn't offer this stream)

## 🗺️ Obtaining School Data

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
- Output to `data/schools.csv`

Copy the generated file:
```bash
cp data/schools.csv school-finder/public/schools.csv
```

**Note**: The scraper may fail if the source website implements bot protection. In this case, you'll need to manually export the data or use an existing dataset.

### Option 2: Manual Data Entry

You can create your own CSV file based on data from:
- Ministry of Education (MOE) website
- School websites
- Education portals like sgschooling.com

### Option 3: Use Sample Data

The repository includes sample data for testing purposes in `public/schools.csv`.

## 🚀 Deployment to GitHub Pages

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

## ⚙️ Configuration

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
zoom={11}  // Line 356

// Default distance filter
const [maxDistance, setMaxDistance] = useState(50); // Line 70

// Map tile provider (currently OneMap)
url="https://www.onemap.gov.sg/maps/tiles/Default/{z}/{x}/{y}.png"  // Line 360
```

### Adding More Towns

Update the `TOWN_COORDS` object in `src/App.jsx`:

```javascript
const TOWN_COORDS = {
  'Your Town': { lat: 1.xxxx, lng: 103.xxxx },
  // ...
};
```

## 📱 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ Internet Explorer: Not supported

## 🔒 Privacy & Data

- **No User Data Collection**: This app runs entirely in your browser
- **No Cookies**: No tracking or analytics
- **External APIs**:
  - OneMap API for geocoding (postal code → coordinates)
  - OneMap tiles for map display
- **Data Source**: School data is scraped from public websites (sgschooling.com)

## 🐛 Known Issues & Limitations

1. **Geocoding Limits**: OneMap API has rate limits. If you make too many postal code lookups quickly, you may get errors.
2. **Browser Caching**: Map tiles are cached by your browser. Use Ctrl+Shift+R to force refresh if maps don't load.
3. **Mobile Performance**: Large datasets may be slower on older mobile devices.
4. **Scraper Reliability**: The web scraper may break if the source website changes structure or blocks automated access.

## 🤝 Contributing

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

## 📄 License

This project is for educational purposes. School data is publicly available information.

- Code: MIT License
- Data: Sourced from public websites (sgschooling.com, MOE)
- Maps: © OneMap (Singapore Land Authority)

## 🙏 Acknowledgments

- **OneMap**: Singapore Land Authority for mapping services
- **sgschooling.com**: Source for school cut-off point data
- **Ministry of Education (MOE)**: Official education data
- **Leaflet**: Open-source mapping library
- **React + Vite**: Modern web development tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/EkChinHui/s1-helper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EkChinHui/s1-helper/discussions)

## 🗺️ Roadmap

- [ ] Add school comparison feature
- [ ] Include CCA (Co-Curricular Activities) information
- [ ] Add school rankings and ratings
- [ ] Include MRT/bus accessibility
- [ ] Mobile app version
- [ ] Export filtered results to PDF
- [ ] Add school photos and virtual tours
- [ ] Integration with MOE School Finder

## 📚 Related Resources

- [MOE Secondary School Posting](https://www.moe.gov.sg/secondary/s1-posting)
- [OneMap API Documentation](https://www.onemap.gov.sg/docs/)
- [Singapore School Information](https://www.moe.gov.sg/schoolfinder)

---

**Made with ❤️ for Singapore students and parents**

*Last Updated: November 2025*
