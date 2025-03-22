import os
import psycopg2
import logging
from psycopg2 import sql, IntegrityError


class DatabaseClient:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.connection = psycopg2.connect(
            dbname=os.getenv('DATABASE_NAME') if os.getenv('DATABASE_NAME') else 'car_prices',
            user=os.getenv('DATABASE_USER') if os.getenv('DATABASE_USER') else 'admin',
            password=os.getenv('DATABASE_PASSWORD') if os.getenv('DATABASE_PASSWORD') else 'password',
            host=os.getenv('DATABASE_HOST') if os.getenv('DATABASE_HOST') else 'localhost',
            port=os.getenv('DATABASE_PORT') if os.getenv('DATABASE_PORT') else '5432'
        )
        self.logger.info("Established connection to database.")

    def execute_and_fetch_all(self, raw_query: str):
        query = sql.SQL(raw_query)
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise e

    def execute(self, raw_query: str):
        query = sql.SQL(raw_query)
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except IntegrityError as e:
            self.connection.rollback()
            cursor.close()
            raise e
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            self.logger.error(f"Database error: {e}")
            raise e
