import logging
from typing import List
from models.school import School
from parsers.main_page_parser import MainPageParser
from parsers.detail_page_parser import DetailPageParser
from utils.http_client import HTTPClient
from utils.rate_limiter import RateLimiter
from utils.csv_writer import CSVWriter
from config import Config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SchoolScraper:
    """Main scraper orchestrator"""

    def __init__(self):
        self.http_client = HTTPClient()
        self.rate_limiter = RateLimiter()
        self.schools: List[School] = []

    def run(self):
        """Execute complete scraping workflow"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Singapore Secondary School Scraper")
            logger.info("=" * 60)

            # Step 1: Scrape main page
            logger.info(f"\n📄 Fetching main page: {Config.MAIN_PAGE_URL}")
            self.schools = self._scrape_main_page()
            logger.info(
                f"✓ Found {len(self.schools)} schools (filtered: no affiliated, no special schools)"
            )

            # Step 2: Scrape detail pages
            logger.info(f"\n📍 Fetching individual school pages for address and historical data...")
            self._scrape_detail_pages()

            # Step 3: Export to CSV
            logger.info(f"\n💾 Exporting to {Config.OUTPUT_FILE}")
            self._export_to_csv()

            logger.info("\n" + "=" * 60)
            logger.info("✓ Scraping completed successfully!")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"\n❌ Scraping failed: {e}", exc_info=True)
            raise
        finally:
            self.http_client.close()

    def _scrape_main_page(self) -> List[School]:
        """Scrape the main cut-off points page"""
        self.rate_limiter.wait()
        response = self.http_client.get(Config.MAIN_PAGE_URL)
        parser = MainPageParser(response.text)
        return parser.parse()

    def _scrape_detail_pages(self):
        """Scrape all individual school detail pages"""
        total = len(self.schools)

        for i, school in enumerate(self.schools, 1):
            try:
                logger.info(f"[{i}/{total}] {school.name}")

                self.rate_limiter.wait()
                response = self.http_client.get(school.detail_url)
                parser = DetailPageParser(response.text)

                town, address, historical_data = parser.parse()
                school.town = town
                school.address = address

                # Update historical cut-off data
                if "2024" in historical_data:
                    school.cutoff_2024_ip = historical_data["2024"].get("ip")
                    school.cutoff_2024_pg3 = historical_data["2024"].get("pg3")
                    school.cutoff_2024_pg2 = historical_data["2024"].get("pg2")
                    school.cutoff_2024_pg1 = historical_data["2024"].get("pg1")

                if "2023" in historical_data:
                    school.cutoff_2023_ip = historical_data["2023"].get("ip")
                    school.cutoff_2023_pg3 = historical_data["2023"].get("pg3")
                    school.cutoff_2023_pg2 = historical_data["2023"].get("pg2")
                    school.cutoff_2023_pg1 = historical_data["2023"].get("pg1")

                logger.info(f"  → {town}, {address}")

            except Exception as e:
                logger.warning(f"  ⚠ Failed to scrape {school.name}: {e}")
                # Continue with other schools
                continue

    def _export_to_csv(self):
        """Export scraped data to CSV"""
        writer = CSVWriter(Config.OUTPUT_FILE)
        writer.write(self.schools)


if __name__ == "__main__":
    scraper = SchoolScraper()
    scraper.run()
