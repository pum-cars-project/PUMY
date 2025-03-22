import httpx
import time
import random
import logging
import traceback
from bs4 import BeautifulSoup

from domain.exceptions import PageNotFoundError, OfferLinkAlreadyInDatabaseError, StageFailedError
from infrastructure.database.database_service import DatabaseService
from utils.wrappers import singleton


@singleton
class OfferLinkScraper:

    ENTRY_POINT = "https://www.otomoto.pl/osobowe/"
    OFFER_URL_PREFIX = "https://www.otomoto.pl/osobowe/oferta/"
    HEADERS = [
            {
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/117.0.0.0 Safari/537.36',
                'Accept':
                    'text/html,application/xhtml+xml,application'
                    '/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                    'q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language':
                    'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer':
                    'https://www.google.com/',
            },
            {
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; '
                    'rv:109.0) Gecko/20100101 Firefox/109.0',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/'
                          'xml;q=0.9,image/avif,image/webp,'
                          'image/apng,*/*;q=0.8',
                'Referer':
                    'https://www.google.com/',
            },
            {
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15;'
                    ' rv:109.0) Gecko/20100101 Firefox/117.0',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'Accept': 'text/html,application/xhtml+xml,'
                          'application/xml;q=0.9,image/avif,'
                          'image/webp,*/*;q=0.8',
                'Referer':
                    'https://www.google.com/',
            }
        ]

    def __init__(self):
        self.database_service = DatabaseService()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def mark_stage_as_failed(self, job, exception):
        job.offer_links_scraping_status["state"] = "Failed"
        job.offer_links_scraping_status["exception"] = exception

    def mark_stage_as_done(self, job):
        job.offer_links_scraping_status["state"] = "Done"

    def update_initial_stage_status(self, job):
        job.stage = "Offer Link Scraping"
        job.offer_links_scraping_status["state"] = "Running"

    def update_job_stage_status(self, job, page_number, read_links_from_page):
        job.offer_links_scraping_status["pages_read"] = page_number
        total = job.offer_links_scraping_status["total_unique_links_read"] + read_links_from_page
        job.offer_links_scraping_status["total_unique_links_read"] = total

    def extract_link_data(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, "lxml")
        anchor_elements = soup.find_all("a", href=True)
        return [anchor['href'] for anchor in anchor_elements if anchor['href'].startswith(self.OFFER_URL_PREFIX)]

    def extract_and_save_links(self, job_id: str, urls: list) -> int:
        total_unique_links = 0
        for url in urls:
            try:
                self.database_service.save_offer_link(job_id, url)
                total_unique_links += 1
            except OfferLinkAlreadyInDatabaseError:
                continue
        return total_unique_links

    # TODO: sprawdzić dlaczego się czasami wypierdala na dużej ilości stron (retry policy?)
    def get_offers_page(self, make: str, page_number: int) -> str:
        url = f"{self.ENTRY_POINT}{make}?page={page_number}"
        header = random.choice(self.HEADERS)
        response = httpx.get(url, headers=header, follow_redirects=True)
        self.logger.info(f"Got response with status code {response.status_code}")
        if response.status_code != 200:
            raise PageNotFoundError()
        return response.text

    def scrape_offer_links(self, job) -> None:
        self.logger.info("Scraping offer links")
        start_time = time.time()
        self.update_initial_stage_status(job)
        page_number = 1
        try:
            while True:
                self.logger.info(f"Current page number: {page_number}")
                html_content = self.get_offers_page("bmw", page_number)
                urls = self.extract_link_data(html_content)
                total_unique_links_from_page = self.extract_and_save_links(job.id, urls)
                self.update_job_stage_status(job, page_number, total_unique_links_from_page)
                page_number += 1
                time.sleep(random.uniform(2, 5))
        except PageNotFoundError:
            self.mark_stage_as_done(job)
            self.logger.info(f"Scraping links took: {time.time() - start_time}")
            return
        except Exception as e:
            self.logger.error(f"Exception occurred while scraping: {e}")
            self.logger.error(traceback.format_exc())
            self.mark_stage_as_failed(job, traceback.format_exc())
            raise StageFailedError()
