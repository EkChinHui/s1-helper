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

    def _scrape_detail_pages(self, preview_count: int = 15):
        """Scrape all individual school detail pages with preview confirmation"""
        total = len(self.schools)

        for i, school in enumerate(self.schools, 1):
            # Pause after preview_count schools for user confirmation
            if i == preview_count + 1:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Preview complete: {preview_count} schools scraped")
                logger.info(f"Remaining: {total - preview_count} schools")
                logger.info("=" * 60)

                response = input("\nContinue scraping remaining schools? [Y/n]: ").strip().lower()
                if response in ['n', 'no']:
                    logger.info("Scraping stopped by user. Exporting preview data...")
                    # Trim schools list to only include scraped ones
                    self.schools = self.schools[:preview_count]
                    return
                logger.info("\nContinuing with remaining schools...\n")

            try:
                logger.info(f"[{i}/{total}] {school.name}")

                self.rate_limiter.wait()
                response = self.http_client.get(school.detail_url)
                parser = DetailPageParser(response.text)

                town, address, historical_data = parser.parse()
                school.town = town
                school.address = address

                # Update historical cut-off data (including 2025 affiliated from detail page)
                if "2025" in historical_data:
                    # Only update affiliated cutoffs for 2025 (non-affiliated comes from main page)
                    school.cutoff_2025_ip_aff = historical_data["2025"].get("ip_aff")
                    school.cutoff_2025_ip_aff_hcl = historical_data["2025"].get("ip_aff_hcl")
                    school.cutoff_2025_pg3_aff = historical_data["2025"].get("pg3_aff")
                    school.cutoff_2025_pg3_aff_hcl = historical_data["2025"].get("pg3_aff_hcl")
                    school.cutoff_2025_pg2_aff = historical_data["2025"].get("pg2_aff")
                    school.cutoff_2025_pg2_aff_hcl = historical_data["2025"].get("pg2_aff_hcl")
                    school.cutoff_2025_pg1_aff = historical_data["2025"].get("pg1_aff")
                    school.cutoff_2025_pg1_aff_hcl = historical_data["2025"].get("pg1_aff_hcl")

                if "2024" in historical_data:
                    school.cutoff_2024_ip = historical_data["2024"].get("ip")
                    school.cutoff_2024_ip_hcl = historical_data["2024"].get("ip_hcl")
                    school.cutoff_2024_pg3 = historical_data["2024"].get("pg3")
                    school.cutoff_2024_pg2 = historical_data["2024"].get("pg2")
                    school.cutoff_2024_pg1 = historical_data["2024"].get("pg1")
                    # Affiliated cutoffs
                    school.cutoff_2024_ip_aff = historical_data["2024"].get("ip_aff")
                    school.cutoff_2024_ip_aff_hcl = historical_data["2024"].get("ip_aff_hcl")
                    school.cutoff_2024_pg3_aff = historical_data["2024"].get("pg3_aff")
                    school.cutoff_2024_pg3_aff_hcl = historical_data["2024"].get("pg3_aff_hcl")
                    school.cutoff_2024_pg2_aff = historical_data["2024"].get("pg2_aff")
                    school.cutoff_2024_pg2_aff_hcl = historical_data["2024"].get("pg2_aff_hcl")
                    school.cutoff_2024_pg1_aff = historical_data["2024"].get("pg1_aff")
                    school.cutoff_2024_pg1_aff_hcl = historical_data["2024"].get("pg1_aff_hcl")

                if "2023" in historical_data:
                    school.cutoff_2023_ip = historical_data["2023"].get("ip")
                    school.cutoff_2023_ip_hcl = historical_data["2023"].get("ip_hcl")
                    school.cutoff_2023_pg3 = historical_data["2023"].get("pg3")
                    school.cutoff_2023_pg2 = historical_data["2023"].get("pg2")
                    school.cutoff_2023_pg1 = historical_data["2023"].get("pg1")
                    # Affiliated cutoffs
                    school.cutoff_2023_ip_aff = historical_data["2023"].get("ip_aff")
                    school.cutoff_2023_ip_aff_hcl = historical_data["2023"].get("ip_aff_hcl")
                    school.cutoff_2023_pg3_aff = historical_data["2023"].get("pg3_aff")
                    school.cutoff_2023_pg3_aff_hcl = historical_data["2023"].get("pg3_aff_hcl")
                    school.cutoff_2023_pg2_aff = historical_data["2023"].get("pg2_aff")
                    school.cutoff_2023_pg2_aff_hcl = historical_data["2023"].get("pg2_aff_hcl")
                    school.cutoff_2023_pg1_aff = historical_data["2023"].get("pg1_aff")
                    school.cutoff_2023_pg1_aff_hcl = historical_data["2023"].get("pg1_aff_hcl")

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
