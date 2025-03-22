from datetime import datetime
from api.jobs import CreateNewJobRequest


class Job:
    def __init__(self, request: CreateNewJobRequest):
        self.id = f"{request.make}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}"
        self.make = request.make
        self.offer_links_scraping_status = None
        self.offers_scraping_status = None
        self.set_offer_links_scraping_status(request.is_offer_links_scraping_expected)
        self.set_offers_scraping_status(request.is_offers_scraping_expected)
        self.stage = "Setup"
        self.status = "Created"

    def set_offer_links_scraping_status(self, is_offer_link_scraping_expected: bool):
        self.offer_links_scraping_status = {
            "expected": is_offer_link_scraping_expected
        }
        if is_offer_link_scraping_expected:
            self.offer_links_scraping_status["pages_read"] = 0
            self.offer_links_scraping_status["total_unique_links_read"] = 0
            self.offer_links_scraping_status["state"] = "Scheduled"

    def set_offers_scraping_status(self, is_offers_scraping_expected: bool):
        self.offers_scraping_status = {
            "expected": is_offers_scraping_expected
        }
        if is_offers_scraping_expected:
            self.offers_scraping_status["successful_reads"] = 0
            self.offers_scraping_status["failed_reads"] = 0
            self.offers_scraping_status["state"] = "Scheduled"
