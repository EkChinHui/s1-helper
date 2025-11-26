import fs from 'fs';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';

// Sleep function to avoid rate limiting
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Geocode an address using Singapore OneMap API
async function geocodeAddress(address) {
  try {
    const encodedAddress = encodeURIComponent(address);
    const url = `https://www.onemap.gov.sg/api/common/elastic/search?searchVal=${encodedAddress}&returnGeom=Y&getAddrDetails=Y&pageNum=1`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.found > 0 && data.results && data.results.length > 0) {
      const result = data.results[0];
      return {
        latitude: parseFloat(result.LATITUDE),
        longitude: parseFloat(result.LONGITUDE),
        found: true
      };
    }

    return { latitude: null, longitude: null, found: false };
  } catch (error) {
    console.error(`Error geocoding address "${address}":`, error.message);
    return { latitude: null, longitude: null, found: false };
  }
}

async function main() {
  console.log('Reading schools.csv...');
  const csvContent = fs.readFileSync('../data/schools.csv', 'utf-8');

  // Parse CSV
  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true
  });

  console.log(`Found ${records.length} schools to geocode\n`);

  // Geocode each school
  for (let i = 0; i < records.length; i++) {
    const school = records[i];
    const address = school.Address;

    console.log(`[${i + 1}/${records.length}] Geocoding: ${school['School Name']}`);
    console.log(`  Address: ${address}`);

    const { latitude, longitude, found } = await geocodeAddress(address);

    if (found) {
      school.Latitude = latitude;
      school.Longitude = longitude;
      console.log(`  ✓ Success: ${latitude}, ${longitude}`);
    } else {
      school.Latitude = '';
      school.Longitude = '';
      console.log(`  ✗ Not found`);
    }

    // Add delay to avoid rate limiting (OneMap allows ~250 requests per minute)
    if (i < records.length - 1) {
      await sleep(300); // 300ms delay between requests
    }

    console.log('');
  }

  // Write updated CSV
  console.log('Writing updated CSV...');
  const output = stringify(records, {
    header: true,
    columns: Object.keys(records[0])
  });

  fs.writeFileSync('../data/schools.csv', output, 'utf-8');
  console.log('Done! Updated schools.csv with coordinates.');

  // Print summary
  const geocodedCount = records.filter(r => r.Latitude && r.Longitude).length;
  console.log(`\nSummary: ${geocodedCount}/${records.length} schools successfully geocoded`);

  if (geocodedCount < records.length) {
    console.log('\nSchools that failed to geocode:');
    records.filter(r => !r.Latitude || !r.Longitude).forEach(school => {
      console.log(`  - ${school['School Name']}: ${school.Address}`);
    });
  }
}

main().catch(console.error);
