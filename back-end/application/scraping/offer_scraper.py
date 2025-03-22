import httpx
from bs4 import BeautifulSoup
import orjson

from domain.exceptions import PageNotFoundError, StageFailedError
from infrastructure.database.database_service import DatabaseService
from utils.wrappers import singleton


@singleton
class OfferScraper:

    IRRELEVANT_DATA_PARAMETERS = {"vin", "date_registration", "registration", "catalog_urn"}

    def __init__(self):
        self.database_service = DatabaseService()

    def extract_car_price(self, price: dict, extracted_car_data: dict) -> None:
        extracted_car_data["price"] = {
            "amount": price["value"],
            "currency": price["currency"]
        }

    def parse_value(self, value):
        if value == "1" or value == "0":
            return bool(int(value))
        return value

    def extract_car_parameters(self, parameters: dict, extracted_car_data: dict) -> None:
        relevant_parameters = [value for key, value in parameters.items() if key not in self.IRRELEVANT_DATA_PARAMETERS]
        for value in relevant_parameters:
            extracted_car_data[value["label"]] = self.parse_value(value["values"][0]["value"])

    def extract_car_data(self, offer_data: dict) -> dict:
        extracted_car_data = dict()
        extracted_car_data["id"] = offer_data["id"]
        self.extract_car_parameters(offer_data["parametersDict"], extracted_car_data)
        self.extract_car_price(offer_data["price"], extracted_car_data)
        return extracted_car_data

    def extract_offer_data(self, html_content: str) -> dict:
        soup = BeautifulSoup(html_content, "lxml")
        data_element = soup.find("script", {"id": "__NEXT_DATA__"})
        json_data = orjson.loads(data_element.decode_contents())
        return json_data["props"]["pageProps"]["advert"]

    def get_offer_page(self, url: str) -> str:
        response = httpx.get(url)
        if response.status_code != 200:
            raise PageNotFoundError()
        return response.text

    def get_offer_links(self, job_id: str) -> list:
        offer_links = self.database_service.get_all_offer_links(job_id)
        return [record[0] for record in offer_links]

    def scrape_offers(self, job):
        link_list = self.get_offer_links(job.id)
        total_successes = 0
        total_failures = 0
        for link in link_list:
            try:
                html_content = self.get_offer_page(link)
                extracted_offer_data = self.extract_offer_data(html_content)
                car_data = self.extract_car_data(extracted_offer_data)
                self.database_service.save_car(job.id, car_data)
                total_successes += 1
            except PageNotFoundError:
                total_failures += 1
                continue
            except Exception:
                raise StageFailedError()
