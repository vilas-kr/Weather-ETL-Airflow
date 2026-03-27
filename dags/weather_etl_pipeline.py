import requests
import logging
import pendulum
from datetime import timedelta, datetime
 
from airflow.sdk import dag, task, Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.timetables.trigger import CronTriggerTimetable
from psycopg2 import OperationalError, DatabaseError, InterfaceError

logger = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Kolkata")

DEFAULT_ARGS = {
    "retries": 3,
    "retry_delay": timedelta(seconds=10),
}

@dag(
    dag_id="weather_etl",
    start_date=pendulum.datetime(2026, 1, 1, tz=local_tz),
    schedule=CronTriggerTimetable("0 6 * * *", timezone=local_tz),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["Weather"]
)
def weather_etl():
    
    @task
    def extract_weather_data():
        url = "http://api.openweathermap.org/data/2.5/weather"
        api_key = Variable.get("WEATHER_API_KEY")
        city = Variable.get("CITY")

        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.error(f"{city} API failed: {response.text}")
                raise ValueError(f"{city} API error {response.status_code}")

            data = response.json()

            if "main" not in data:
                raise ValueError(f"{city} invalid response")

            logger.info(f"Extracted data for {city}")
            return data

        except Exception as e:
            logger.error(f"{city} extraction failed: {e}")
            raise
        
    @task
    def transform_weather_data(data: dict):
        try:
            return {
                "city_name": data["name"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "load_time": pendulum.from_timestamp(data["dt"], tz="UTC")
            }
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            raise
        
    @task
    def load_weather_data(record: dict):
        hook = PostgresHook(postgres_conn_id="weather_postgre_db")

        conn = None
        cursor = None
        
        try:
            conn = hook.get_conn()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    city_name VARCHAR(100),
                    load_time TIMESTAMP WITH TIME ZONE,
                    feels DECIMAL(5,2),
                    temp DECIMAL(5,2),
                    humidity INT
                );
            """)

            insert_query = """
                INSERT INTO weather 
                (city_name, load_time, feels, temp, humidity)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                insert_query, 
                (
                    record['city_name'],
                    record['load_time'],
                    record['feels_like'],
                    record['temp'],
                    record['humidity']
                )
            )

            conn.commit()
            logger.info(f"Inserted weather data for {record['city_name']}")

        # Database error
        except (OperationalError, InterfaceError) as e:
            logger.error(f"Database connection error: {e}")
            raise

        # query and transcation errors
        except DatabaseError as e:
            if conn:
                conn.rollback()
            logger.error(f"Database query failed, rolled back: {e}")
            raise

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error during load: {e}")
            raise

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Pipeline flow
    extract = extract_weather_data()
    transform = transform_weather_data(extract)
    load_weather_data(transform)

# Instantiating the DAG
weather_etl()