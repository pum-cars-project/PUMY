import concurrent.futures
import logging

from infrastructure.database.database_service import DatabaseService
from utils.wrappers import singleton
from .job import Job
from .scraping.offer_link_scraper import OfferLinkScraper
from .scraping.offer_scraper import OfferScraper
from api.jobs import CreateNewJobRequest
from domain.exceptions import StageFailedError


@singleton
class PipelineService:
    def __init__(self):
        self.database_service = DatabaseService()
        self.current_job = None
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.offer_link_scraper = OfferLinkScraper()
        self.offer_scraper = OfferScraper()

    def create_new_job(self, request: CreateNewJobRequest) -> str:
        self.logger.info(f"Got job request for make: {request.make}")
        self.current_job = Job(request)
        self.pool.submit(self.execute, self.current_job)
        return self.current_job.id

    def get_job_status(self, job_id: str) -> Job:
        if self.current_job is None:
            return { "message": "no job found" }
        return self.current_job

    def execute(self, job: Job) -> None:
        job.status = "Running"
        self.logger.info(f"Job: {job.id} is running...")
        try:
            self.dispatch_offer_links_scraping(job)
            self.dispatch_offers_scraping(job)
        except StageFailedError:
            job.status = "Failed"
            self.logger.error(f"Job: {job.id} has failed")
            return
        job.status = "Done"
        self.logger.info(f"Job: {job.id} is done")

    def dispatch_offer_links_scraping(self, job: Job) -> None:
        if job.offer_links_scraping_status["expected"]:
            self.logger.info(f"Job: {job.id} has started offer link scraping")
            self.database_service.create_offer_links_table(job.id)
            self.offer_link_scraper.scrape_offer_links(job)
        else:
            self.logger.info(f"Job: {job.id} is not required to scrape offer links, skipping...")

    def dispatch_offers_scraping(self, job: Job) -> None:
        if job.offers_scraping_status["expected"]:
            self.logger.info(f"Job: {job.id} has started offers scraping")
            self.database_service.create_cars_table(job.id)
            self.offer_scraper.scrape_offers(job)
        else:
            self.logger.info(f"Job: {job.id} is not required to scrape offers, skipping...")

    # not implemented
    def dispatch_training(self, job: Job) -> None:
        pass
