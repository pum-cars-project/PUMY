import logging
from .database_client import DatabaseClient
from utils.wrappers import singleton
from psycopg2 import IntegrityError
from domain.exceptions import OfferLinkAlreadyInDatabaseError


@singleton
class DatabaseService:
    links_table_suffix = "_offer_links"
    cars_table_suffix = "_cars"

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.client = DatabaseClient()

    def create_offer_links_table(self, job_id: str) -> None:
        table_name = job_id + self.links_table_suffix
        query = f"""
            CREATE TABLE {table_name} (
                url VARCHAR(255) PRIMARY KEY 
            );
        """
        self.client.execute(query)
        self.logger.info(f"Created table: {table_name}")

    def save_offer_link(self, job_id: str, url: str) -> None:
        table_name = job_id + self.links_table_suffix
        query = f"""
            INSERT INTO {table_name} VALUES ('{url}');
        """
        try:
            self.client.execute(query)
        except IntegrityError:
            raise OfferLinkAlreadyInDatabaseError()

    def get_all_offer_links(self, job_id: str) -> list:
        table_name = job_id + self.links_table_suffix
        query = f"""
            SELECT url FROM {table_name}
        """
        return self.client.execute(query)

# need more info on the data frame
    def create_cars_table(self, job_id: str) -> None:
        table_name = job_id + self.cars_table_suffix
        query = f"""
            CREATE TABLE {table_name} (
                id VARCHAR(12) PRIMARY KEY
            );
        """
        self.client.execute(query)

    def save_car(self, job_id: str, car: dict) -> None:
        table_name = job_id + self.cars_table_suffix
        query = f"""
            INSERT INTO {table_name} VALUES ('{car.id}');
        """
        try:
            self.client.execute(query)
        except IntegrityError:
            raise OfferLinkAlreadyInDatabaseError()