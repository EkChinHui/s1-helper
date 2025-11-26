import { useState, useEffect } from 'react'
import { getDistance } from 'geolib'
import { MapContainer, TileLayer, Marker, Popup, Circle, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'

// Fix Leaflet default marker icons
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const UserIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [35, 57],
  iconAnchor: [17, 57],
  className: 'user-marker'
});

L.Marker.prototype.options.icon = DefaultIcon;

// Singapore towns with approximate coordinates for distance calculation
const TOWN_COORDS = {
  'Toa Payoh': { lat: 1.3341, lng: 103.8561 },
  'Bukit Timah': { lat: 1.3294, lng: 103.8008 },
  'Bishan': { lat: 1.3526, lng: 103.8352 },
  'Queenstown': { lat: 1.2942, lng: 103.8062 },
  'Kallang': { lat: 1.3116, lng: 103.8636 },
  'Jurong West': { lat: 1.3404, lng: 103.7090 },
  'Novena': { lat: 1.3202, lng: 103.8437 },
  'Tampines': { lat: 1.3537, lng: 103.9447 },
  'Ang Mo Kio': { lat: 1.3691, lng: 103.8454 },
  'Bukit Merah': { lat: 1.2824, lng: 103.8235 },
  'Marine Parade': { lat: 1.3020, lng: 103.9061 },
  'Bedok': { lat: 1.3236, lng: 103.9273 },
  'Seng Kang': { lat: 1.3868, lng: 103.8914 },
  'Hougang': { lat: 1.3612, lng: 103.8864 },
  'Choa Chu Kang': { lat: 1.3840, lng: 103.7470 },
  'Woodlands': { lat: 1.4382, lng: 103.7891 },
  'Pasir Ris': { lat: 1.3721, lng: 103.9474 },
  'Serangoon': { lat: 1.3554, lng: 103.8679 },
  'Punggol': { lat: 1.4043, lng: 103.9021 },
  'Geylang': { lat: 1.3201, lng: 103.8918 },
  'Jurong East': { lat: 1.3329, lng: 103.7436 },
  'Bukit Batok': { lat: 1.3590, lng: 103.7537 },
  'Bukit Panjang': { lat: 1.3774, lng: 103.7719 },
  'Yishun': { lat: 1.4304, lng: 103.8354 },
  'Clementi': { lat: 1.3162, lng: 103.7649 },
  'Sembawang': { lat: 1.4491, lng: 103.8185 },
  'Central': { lat: 1.2897, lng: 103.8500 },
};

function App() {
  const [schools, setSchools] = useState([]);
  const [filteredSchools, setFilteredSchools] = useState([]);
  const [selectedStream, setSelectedStream] = useState('IP');
  const [myScore, setMyScore] = useState(4);
  const [maxCutoff, setMaxCutoff] = useState(22);
  const [selectedTown, setSelectedTown] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [userLocation, setUserLocation] = useState(null); // {lat, lng}
  const [locationError, setLocationError] = useState('');
  const [maxDistance, setMaxDistance] = useState(50); // km

  useEffect(() => {
    // Load and parse CSV
    fetch('/schools.csv')
      .then(response => response.text())
      .then(text => {
        const lines = text.split('\n');
        const headers = lines[0].split(',');

        const parsed = lines.slice(1)
          .filter(line => line.trim())
          .map(line => {
            const values = line.split(',');
            const school = {};
            headers.forEach((header, i) => {
              school[header.trim()] = values[i]?.trim() || '';
            });
            return school;
          });

        setSchools(parsed);
        setFilteredSchools(parsed);
      });
  }, []);

  // Geocode postal code using OneMap API
  const geocodePostalCode = async () => {
    if (!postalCode || postalCode.length !== 6) {
      setLocationError('Please enter a valid 6-digit postal code');
      return;
    }

    try {
      setLocationError('');
      const response = await fetch(
        `https://www.onemap.gov.sg/api/common/elastic/search?searchVal=${postalCode}&returnGeom=Y&getAddrDetails=Y`
      );
      const data = await response.json();

      if (data.found > 0 && data.results && data.results.length > 0) {
        const result = data.results[0];
        const lat = parseFloat(result.LATITUDE);
        const lng = parseFloat(result.LONGITUDE);
        setUserLocation({ lat, lng });
        setSelectedTown(''); // Clear town selection
        setLocationError('');
      } else {
        setLocationError('Postal code not found');
        setUserLocation(null);
      }
    } catch (error) {
      setLocationError('Error geocoding postal code');
      console.error(error);
    }
  };

  useEffect(() => {
    // Apply filters
    let filtered = schools;

    // Filter by AL score using selected stream
    filtered = filtered.filter(school => {
      const scoreField = `2025_${selectedStream}`;
      const score = school[scoreField];

      // Exclude schools that don't have cut-off points for this stream
      if (!score || score === '-' || score === '--') return false;

      // Extract numeric value from score
      let numericScore;
      const digitsOnly = score.replace(/[^\d]/g, '');

      if (selectedStream === 'IP') {
        // IP scores are simple: "7M-" -> 7, "6-" -> 6
        numericScore = parseInt(digitsOnly);
      } else {
        // PG scores can be ranges like "2125" (21-25) or "922" (9-22)
        // Extract the minimum score (first 1-2 digits)
        if (digitsOnly.length === 4) {
          // e.g., "2125" -> 21, "2628" -> 26
          numericScore = parseInt(digitsOnly.substring(0, 2));
        } else if (digitsOnly.length === 3) {
          // e.g., "922" -> 9
          numericScore = parseInt(digitsOnly.substring(0, 1));
        } else {
          // Single or double digit
          numericScore = parseInt(digitsOnly);
        }
      }

      return !isNaN(numericScore) && numericScore >= myScore && numericScore <= maxCutoff;
    });

    // Filter by location proximity
    const effectiveLocation = userLocation || (selectedTown && TOWN_COORDS[selectedTown]);

    if (effectiveLocation) {
      filtered = filtered.filter(school => {
        // Use precise school coordinates if available
        const schoolLat = parseFloat(school.Latitude);
        const schoolLng = parseFloat(school.Longitude);

        if (!schoolLat || !schoolLng || isNaN(schoolLat) || isNaN(schoolLng)) {
          return false;
        }

        // getDistance returns distance in meters, convert to km
        const distanceInMeters = getDistance(
          { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
          { latitude: schoolLat, longitude: schoolLng }
        );
        const distanceInKm = distanceInMeters / 1000;

        return distanceInKm <= maxDistance;
      });
    }

    setFilteredSchools(filtered);
  }, [schools, selectedStream, myScore, maxCutoff, selectedTown, userLocation, maxDistance]);

  const getScoreDisplay = (school) => {
    const currentYear = `2025_${selectedStream}`;
    const prevYear = `2024_${selectedStream}`;
    const prevYear2 = `2023_${selectedStream}`;
    return school[currentYear] || school[prevYear] || school[prevYear2] || 'N/A';
  };

  const effectiveLocation = userLocation || (selectedTown && TOWN_COORDS[selectedTown]);

  return (
    <div className="app">
      <header>
        <h1>Singapore Secondary School Finder</h1>
        <p>Filter schools by AL score and location</p>
      </header>

      <div className="filters">
        <div className="filter-group">
          <label>
            Program Stream:
            <select
              value={selectedStream}
              onChange={(e) => setSelectedStream(e.target.value)}
            >
              <option value="IP">Integrated Programme (IP)</option>
              <option value="PG1">Phase 1 (PG1)</option>
              <option value="PG2">Phase 2 (PG2)</option>
              <option value="PG3">Phase 3 (PG3)</option>
            </select>
          </label>
        </div>

        <div className="filter-group">
          <label>
            Your AL Score (2025 {selectedStream}): {myScore}
            <input
              type="range"
              min="4"
              max="22"
              value={myScore}
              onChange={(e) => setMyScore(parseInt(e.target.value))}
            />
          </label>
          <p className="filter-hint">Show schools you can get into (cut-off ≥ {myScore})</p>
        </div>

        <div className="filter-group">
          <label>
            Maximum School Cut-off (2025 {selectedStream}): {maxCutoff}
            <input
              type="range"
              min="4"
              max="22"
              value={maxCutoff}
              onChange={(e) => setMaxCutoff(parseInt(e.target.value))}
            />
          </label>
          <p className="filter-hint">Filter out schools that are too easy (cut-off ≤ {maxCutoff})</p>
        </div>

        <div className="filter-group">
          <label>Your Location:</label>
          <div className="location-options">
            <div className="location-method">
              <label>Town:
                <select
                  value={selectedTown}
                  onChange={(e) => {
                    setSelectedTown(e.target.value);
                    setUserLocation(null);
                    setPostalCode('');
                  }}
                >
                  <option value="">Select a town</option>
                  {Object.keys(TOWN_COORDS).sort().map(town => (
                    <option key={town} value={town}>{town}</option>
                  ))}
                </select>
              </label>
            </div>

            <div className="location-divider">OR</div>

            <div className="location-method">
              <label>Postal Code:
                <div className="postal-input">
                  <input
                    type="text"
                    value={postalCode}
                    onChange={(e) => setPostalCode(e.target.value)}
                    placeholder="Enter 6-digit postal code"
                    maxLength="6"
                  />
                  <button onClick={geocodePostalCode} className="locate-btn">
                    Locate
                  </button>
                </div>
              </label>
              {locationError && <p className="error-message">{locationError}</p>}
            </div>
          </div>

          {userLocation && (
            <p className="location-status">
              📍 Using coordinates: {userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}
            </p>
          )}
        </div>

        {effectiveLocation && (
          <div className="filter-group">
            <label>
              Maximum Distance: {maxDistance} km
              <input
                type="range"
                min="1"
                max="50"
                value={maxDistance}
                onChange={(e) => setMaxDistance(parseInt(e.target.value))}
              />
            </label>
          </div>
        )}
      </div>

      <div className="results">
        <h2>Found {filteredSchools.length} schools</h2>

        <div className="schools-grid">
          {filteredSchools.map((school, index) => (
            <div key={index} className="school-card">
              <h3>{school['School Name']}</h3>
              <div className="school-info">
                <p><strong>Town:</strong> {school.Town}</p>
                <p><strong>Address:</strong> {school.Address}</p>
                <p><strong>2025 AL Score ({selectedStream}):</strong> {getScoreDisplay(school)}</p>
                {effectiveLocation && school.Latitude && school.Longitude && (
                  <p><strong>Distance:</strong> {
                    (getDistance(
                      { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
                      { latitude: parseFloat(school.Latitude), longitude: parseFloat(school.Longitude) }
                    ) / 1000).toFixed(1)
                  } km</p>
                )}
              </div>
              <a
                href={school['Detail URL']}
                target="_blank"
                rel="noopener noreferrer"
                className="details-link"
              >
                View Details →
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Map View */}
      {effectiveLocation && filteredSchools.length > 0 && (
        <div className="map-view">
          <h2>Map View ({filteredSchools.length} schools within {maxDistance} km)</h2>
          <div className="map-container-results">
            <MapContainer
              center={[effectiveLocation.lat, effectiveLocation.lng]}
              zoom={11}
              style={{ height: '600px', width: '100%' }}
            >
              <TileLayer
                url="https://www.onemap.gov.sg/maps/tiles/Default/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.onemap.gov.sg/">OneMap</a>'
              />

              {/* User location marker */}
              <Marker position={[effectiveLocation.lat, effectiveLocation.lng]} icon={UserIcon}>
                <Popup>
                  <div className="map-popup">
                    <h4>📍 Your Location</h4>
                    <p>{effectiveLocation.lat.toFixed(4)}, {effectiveLocation.lng.toFixed(4)}</p>
                  </div>
                </Popup>
              </Marker>

              {/* Distance radius circle */}
              <Circle
                center={[effectiveLocation.lat, effectiveLocation.lng]}
                radius={maxDistance * 1000} // Convert km to meters
                pathOptions={{
                  color: '#3498db',
                  fillColor: '#3498db',
                  fillOpacity: 0.1,
                  weight: 2
                }}
              />

              {/* School markers */}
              {filteredSchools.map((school, index) => {
                const schoolLat = parseFloat(school.Latitude);
                const schoolLng = parseFloat(school.Longitude);

                if (!schoolLat || !schoolLng || isNaN(schoolLat) || isNaN(schoolLng)) {
                  return null;
                }

                const distance = (getDistance(
                  { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
                  { latitude: schoolLat, longitude: schoolLng }
                ) / 1000).toFixed(1);

                return (
                  <Marker
                    key={index}
                    position={[schoolLat, schoolLng]}
                  >
                    <Tooltip
                      permanent
                      direction="right"
                      offset={[10, 0]}
                      className="school-tooltip"
                    >
                      {school['School Name']}
                    </Tooltip>
                    <Popup>
                      <div className="map-popup">
                        <h4>{school['School Name']}</h4>
                        <p><strong>Town:</strong> {school.Town}</p>
                        <p><strong>Address:</strong> {school.Address}</p>
                        <p><strong>AL Score ({selectedStream}):</strong> {getScoreDisplay(school)}</p>
                        <p><strong>Distance:</strong> {distance} km</p>
                        <a
                          href={school['Detail URL']}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="popup-link"
                        >
                          View Details →
                        </a>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
