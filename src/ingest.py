
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load database credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Missing database settings in .env")

# Create the PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql+psycopg2://{quote_plus(DB_USER)}:"
    f"{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# NYC 311 Open Data API
API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

params = {
    "$limit": 10000,
    "$select": (
        "unique_key,created_date,closed_date,agency,"
        "complaint_type,borough,status,incident_zip"
    ),
    "$where": (
        "created_date >= '2025-01-01T00:00:00' "
        "AND created_date < '2025-02-01T00:00:00'"
    )
}

def main():
    print("Fetching NYC 311 records...")

    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    if df.empty:
        raise ValueError("The API returned no records.")

    print(f"Records fetched: {len(df)}")

    engine = create_engine(DATABASE_URL)

    try:
        df.to_sql(
            name="311_service_requests",
            con=engine,
            schema="public",
            if_exists="replace",
            index=False
        )

        print("Data loaded successfully!")
        print(f"Rows loaded: {len(df)}")
        print("PostgreSQL table: public.311_service_requests")

    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
