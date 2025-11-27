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
  'Tengah': { lat: 1.3644, lng: 103.7200 },
  'Central': { lat: 1.2897, lng: 103.8500 },
};

// Get eligible posting groups based on AL score (MOE official mappings)
const getEligibleGroups = (score) => {
  if (score <= 20) return ['PG3', 'IP'];  // G3 + IP eligible
  if (score <= 22) return ['PG2', 'PG3']; // G2 or G3
  if (score <= 24) return ['PG2'];        // G2 only
  if (score === 25) return ['PG1', 'PG2']; // G1 or G2
  return ['PG1'];  // 26-30: G1 only
};

// Display names for posting groups
const GROUP_DISPLAY_NAMES = {
  'IP': 'IP',
  'PG1': 'PG1',
  'PG2': 'PG2',
  'PG3': 'PG3'
};

function App() {
  const [schools, setSchools] = useState([]);
  const [filteredSchools, setFilteredSchools] = useState([]);
  const [myScore, setMyScore] = useState(10);
  const [maxCutoff, setMaxCutoff] = useState(30);
  const [selectedTown, setSelectedTown] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [userLocation, setUserLocation] = useState(null); // {lat, lng}
  const [locationError, setLocationError] = useState('');
  const [maxDistance, setMaxDistance] = useState(50); // km
  const [useHistoricalMax, setUseHistoricalMax] = useState(false);
  const [affiliatedSchool, setAffiliatedSchool] = useState(''); // School name the student is affiliated with
  const [genderFilter, setGenderFilter] = useState('all'); // 'all', 'mixed', 'boys', 'girls'
  const [sortBy, setSortBy] = useState('name'); // 'name' or 'distance'
  const [hmtFilter, setHmtFilter] = useState([]); // ['HCL', 'HTL', 'HML']

  // Helper function to extract numeric score from score string
  const extractNumericScore = (score, stream) => {
    if (!score || score === '-' || score === '--') return null;
    const digitsOnly = score.replace(/[^\d]/g, '');
    if (!digitsOnly) return null;

    if (stream === 'IP') {
      return parseInt(digitsOnly);
    } else {
      if (digitsOnly.length === 4) {
        return parseInt(digitsOnly.substring(0, 2));
      } else if (digitsOnly.length === 3) {
        return parseInt(digitsOnly.substring(0, 1));
      } else {
        return parseInt(digitsOnly);
      }
    }
  };

  // Helper function to get the column name for a group
  // Uses affiliated suffix only if this school is the student's affiliated school
  const getColumnName = (year, group, schoolName) => {
    // IP doesn't have affiliated cutoffs
    if (group === 'IP') {
      return `${year}_${group}`;
    }
    // For PG1, PG2, PG3 - use affiliated column only for the student's affiliated school
    if (affiliatedSchool && schoolName === affiliatedSchool) {
      return `${year}_${group}_Aff`;
    }
    return `${year}_${group}`;
  };

  // Helper function to get school gender type from CSV data
  const getSchoolGender = (school) => {
    return school.Gender || 'mixed';
  };

  // Get list of schools that have affiliated cutoff data
  const getSchoolsWithAffiliation = () => {
    return schools
      .filter(school => {
        // Check if school has any affiliated cutoff data
        const hasAffData = ['2025', '2024', '2023'].some(year =>
          ['PG1', 'PG2', 'PG3'].some(group => {
            const val = school[`${year}_${group}_Aff`];
            return val && val !== '-' && val !== '--';
          })
        );
        return hasAffData;
      })
      .map(school => school['School Name'])
      .sort();
  };

  useEffect(() => {
    // Load and parse CSV
    fetch(import.meta.env.BASE_URL + 'schools.csv')
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

  // Get eligible groups based on current score
  const eligibleGroups = getEligibleGroups(myScore);

  useEffect(() => {
    // Apply filters
    let filtered = schools;
    const groups = getEligibleGroups(myScore);

    // Filter by AL score - show schools user can get into for any eligible group
    filtered = filtered.filter(school => {
      const schoolName = school['School Name'];
      // Check each eligible group
      for (const group of groups) {
        let numericScore;

        if (useHistoricalMax) {
          // Get scores from all 3 years and use the maximum
          const years = ['2025', '2024', '2023'];
          const scores = years
            .map(year => {
              const colName = getColumnName(year, group, schoolName);
              return extractNumericScore(school[colName], group);
            })
            .filter(s => s !== null && !isNaN(s));

          if (scores.length > 0) {
            numericScore = Math.max(...scores);
          }
        } else {
          // Use 2025 only
          const colName = getColumnName('2025', group, schoolName);
          numericScore = extractNumericScore(school[colName], group);
        }

        // If school has a valid COP for this group and user qualifies
        if (numericScore !== null && !isNaN(numericScore)) {
          if (myScore <= numericScore && numericScore <= maxCutoff) {
            return true;
          }
        }
      }
      return false;
    });

    // Filter by gender type
    if (genderFilter !== 'all') {
      filtered = filtered.filter(school => {
        const schoolGender = getSchoolGender(school);
        return schoolGender === genderFilter;
      });
    }

    // Filter by Higher Mother Tongue languages
    if (hmtFilter.length > 0) {
      filtered = filtered.filter(school => {
        return hmtFilter.every(lang => school[lang] === 'Y');
      });
    }

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

    // Sort results
    if (sortBy === 'distance' && effectiveLocation) {
      filtered.sort((a, b) => {
        const distA = getDistance(
          { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
          { latitude: parseFloat(a.Latitude), longitude: parseFloat(a.Longitude) }
        );
        const distB = getDistance(
          { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
          { latitude: parseFloat(b.Latitude), longitude: parseFloat(b.Longitude) }
        );
        return distA - distB;
      });
    } else {
      filtered.sort((a, b) => a['School Name'].localeCompare(b['School Name']));
    }

    setFilteredSchools(filtered);
  }, [schools, myScore, maxCutoff, selectedTown, userLocation, maxDistance, useHistoricalMax, affiliatedSchool, genderFilter, sortBy, hmtFilter]);

  const getScoreDisplay = (school) => {
    // Show COP for all eligible groups
    const groups = getEligibleGroups(myScore);
    const schoolName = school['School Name'];
    const scores = [];

    for (const group of groups) {
      const colName = getColumnName('2025', group, schoolName);
      const score = school[colName];
      if (score && score !== '-' && score !== '--') {
        scores.push(`${GROUP_DISPLAY_NAMES[group]}: ${score}`);
      }
    }

    return scores.length > 0 ? scores.join(', ') : 'N/A';
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
            Your AL Score: {myScore}
            <input
              type="range"
              min="4"
              max="30"
              value={myScore}
              onChange={(e) => setMyScore(parseInt(e.target.value))}
            />
          </label>
          <p className="filter-hint">
            Eligible for: {eligibleGroups.map(g => GROUP_DISPLAY_NAMES[g]).join(', ')}
          </p>
        </div>

        <div className="filter-group">
          <label>
            Maximum School Cut-off: {maxCutoff}
            <input
              type="range"
              min="4"
              max="30"
              value={maxCutoff}
              onChange={(e) => setMaxCutoff(parseInt(e.target.value))}
            />
          </label>
          <p className="filter-hint">Filter out schools that are too easy (cut-off ≤ {maxCutoff})</p>
        </div>

        <div className="filter-group">
          <label>
            School Type:
            <select
              value={genderFilter}
              onChange={(e) => setGenderFilter(e.target.value)}
            >
              <option value="all">All schools</option>
              <option value="mixed">Co-ed (Mixed)</option>
              <option value="boys">Boys</option>
              <option value="girls">Girls</option>
            </select>
          </label>
        </div>

        <div className="filter-group">
          <label>Higher Mother Tongue Languages:</label>
          <div className="hmt-checkboxes">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={hmtFilter.includes('HCL')}
                onChange={(e) => {
                  if (e.target.checked) {
                    setHmtFilter([...hmtFilter, 'HCL']);
                  } else {
                    setHmtFilter(hmtFilter.filter(l => l !== 'HCL'));
                  }
                }}
              />
              Higher Chinese
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={hmtFilter.includes('HTL')}
                onChange={(e) => {
                  if (e.target.checked) {
                    setHmtFilter([...hmtFilter, 'HTL']);
                  } else {
                    setHmtFilter(hmtFilter.filter(l => l !== 'HTL'));
                  }
                }}
              />
              Higher Tamil
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={hmtFilter.includes('HML')}
                onChange={(e) => {
                  if (e.target.checked) {
                    setHmtFilter([...hmtFilter, 'HML']);
                  } else {
                    setHmtFilter(hmtFilter.filter(l => l !== 'HML'));
                  }
                }}
              />
              Higher Malay
            </label>
          </div>
          <p className="filter-hint">
            Filter schools that offer these Higher Mother Tongue languages
          </p>
        </div>

        <div className="filter-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useHistoricalMax}
              onChange={(e) => setUseHistoricalMax(e.target.checked)}
            />
            Use historical maximum cut-off
          </label>
          <p className="filter-hint">
            Include schools if their cut-off was high enough in any of the past 3 years (2023-2025)
          </p>
        </div>

        <div className="filter-group">
          <label>
            Affiliated Secondary School:
            <select
              value={affiliatedSchool}
              onChange={(e) => setAffiliatedSchool(e.target.value)}
            >
              <option value="">None (not affiliated)</option>
              {getSchoolsWithAffiliation().map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </label>
          <p className="filter-hint">
            If you're from an affiliated primary school, select the secondary school to use easier cut-off points for that school only
          </p>
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
          <>
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

            <div className="filter-group">
              <label>
                Sort by:
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="name">Name (A-Z)</option>
                  <option value="distance">Distance (nearest first)</option>
                </select>
              </label>
            </div>
          </>
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
                {effectiveLocation && school.Latitude && school.Longitude && (
                  <p><strong>Distance:</strong> {
                    (getDistance(
                      { latitude: effectiveLocation.lat, longitude: effectiveLocation.lng },
                      { latitude: parseFloat(school.Latitude), longitude: parseFloat(school.Longitude) }
                    ) / 1000).toFixed(1)
                  } km</p>
                )}
                {(school.HCL === 'Y' || school.HTL === 'Y' || school.HML === 'Y') && (
                  <p><strong>Higher MT:</strong> {[
                    school.HCL === 'Y' && 'Chinese',
                    school.HTL === 'Y' && 'Tamil',
                    school.HML === 'Y' && 'Malay'
                  ].filter(Boolean).join(', ')}</p>
                )}
              </div>
              <div className="cop-history">
                <h4>Cut-Off Points (COP){affiliatedSchool === school['School Name'] ? ' - Affiliated' : ''}</h4>
                <table className="cop-table">
                  <thead>
                    <tr>
                      <th>Year</th>
                      {eligibleGroups.map(group => (
                        <th key={group}>{GROUP_DISPLAY_NAMES[group]}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {['2025', '2024', '2023'].map(year => (
                      <tr key={year}>
                        <td>{year}</td>
                        {eligibleGroups.map(group => {
                          const colName = getColumnName(year, group, school['School Name']);
                          return <td key={group}>{school[colName] || '-'}</td>;
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
                        <p><strong>Distance:</strong> {distance} km</p>
                        <div className="popup-cop">
                          <strong>2025 COP:</strong> {getScoreDisplay(school)}
                        </div>
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
