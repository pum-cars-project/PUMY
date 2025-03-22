from pydantic import BaseModel


class CreateNewJobRequest(BaseModel):
    make: str
    is_offer_links_scraping_expected: bool
    is_offers_scraping_expected: bool
    is_training_expected: bool


class CreateNewJobResponse(BaseModel):
    job_id: str


class JobStatusRequest(BaseModel):
    status: str
