# Weather ETL Pipeline (Apache Airflow)

## Project Overview
This project implements a production-style ETL pipeline using Apache Airflow to fetch real-time weather data from the OpenWeather API, transform it, and store it in a PostgreSQL database.

## Tech Stack
- Python
- Apache Airflow
- PostgreSQL
- Docker (optional but recommended)
- OpenWeather API
- Requests, Pendulum, Psycopg2

## ETL Workflow
### 1. Extract
- Fetch weather data from OpenWeather API
- Uses Airflow Variables for API key and city

### 2. Transform
Processes and formats the data:
- City name
- Temperature
- Feels like temperature
- Humidity
- Load timestamp

### 3. Load
- Store data into PostgreSQL
- Creates table if not exists
- Inserts transformed records

## Project Structure
```
Weather-ETL-Airflow
|
|-- dags/
|   |-- weather_etl_pipeline.py
|
|-- .env
|-- .gitignore
|-- docker-compose.yaml
|-- README.md
|-- requirements.txt
```

## Installation Guide
### Step 1: Clone Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/Weather-ETL-Airflow.git
cd Weather-ETL-Airflow
```

### Step 2: Set Up Environment Variables
Create a `.env` file in the project root with the following content:
```
echo AIRFLOW_UID=50000 > .env
```
### Step 3: Create virtual environment (optional but recommended)
```bash
python -m venv venv
source venv\Scripts\activate  # On Windows
```

### Step 4: Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Start Airflow Services
If you have Docker installed, you can use the provided `docker-compose.yaml` to set up Airflow and PostgreSQL:
```bash
docker-compose up -d
```

### Step 6: Access Airflow UI
Open your web browser and navigate to `http://localhost:8080` to access the Airflow UI. 
Use the default credentials:
- username: `airflow`
- password: `airflow`


### Step 7: PostgreSQL Setup
You can connect to the PostgreSQL database using the following credentials:
```bash
docker exec -it <your_postgres_container> psql -U airflow -d airflow
```
you can find your_postgres_container by running `docker ps` and looking for the container name that corresponds to PostgreSQL.

Create database 'weather_db'
```sql
CREATE DATABASE weather_db;
\l
``` 

### Step 8: Airflow Setup Requirements
1. Create Airflow Variables
    Go to Airflow UI → Admin → Variables and add:

    |Key | Value|
    |-------------|----------------|
    |WEATHER_API_KEY | your_api_key |
    |CITY | Bangalore |

    To get your OpenWeather API key, sign up at [OpenWeather](https://openweathermap.org/api) and create an API key.

2. Create Airflow Connections
    Go to Airflow UI → Admin → Connections and add:
    - connection_id: `weather_postgre_db`
    - connection_type: `Postgres`
    - host: `IP address of your PostgreSQL server `
    steps to find IP address of PostgreSQL server:
        - If using Docker, run `docker ps` to find your PostgreSQL container ID, then execute `docker inspect <container_id> | findstr "IPAddress"` to get the IP address.
    - schema: `weather_db`
    - login: `airflow`
    - password: `airflow`
    - port: `5432`

### Step 9: Trigger the DAG
In the Airflow UI, navigate to the "DAGs" tab, find `weather_etl_pipeline`, and click the toggle to enable it. You can also trigger it manually by clicking the "Trigger DAG" button.

### Step 10: Monitor Execution
Go to Graph View
Click tasks → View Logs to see the logs for each task.

### Step 11: Stop Airflow Services
If you used Docker, you can stop the services with:
```bash
docker-compose down
``` 

## Scheduling
The DAG runs daily at 6:00 AM IST:
- cron : `0 6 * * *`

## Error Handling
- Retries: 3 times
- Retry delay: 10 seconds
- Handles:
    - API failures
    - Invalid responses
    - Database connection issues
    - Transaction rollback on failure

## Features
- Modular ETL design
- Robust error handling
- Airflow Variables support
- Automatic table creation
- Timezone-aware scheduling (IST)

## Author
```
Name: Vilas K R
GitHub: https://github.com/vilas-kr
```






