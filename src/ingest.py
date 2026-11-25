
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load database credentials
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Missing database settings in .env")

# PostgreSQL connection
DATABASE_URL = (
    f"postgresql+psycopg2://{quote_plus(DB_USER)}:"
    f"{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# NYC 311 API
API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# Maximum records per API request
PAGE_SIZE = 10000

# January 2025 dataset
BASE_PARAMS = {
    "$select": (
        "unique_key,created_date,closed_date,agency,"
        "complaint_type,borough,status,incident_zip"
    ),
    "$where": (
        "created_date >= '2025-01-01T00:00:00' "
        "AND created_date < '2025-02-01T00:00:00'"
    ),
    "$order": "created_date ASC, unique_key ASC"
}


def fetch_all_records():

    all_records = []
    offset = 0

    print("Fetching NYC 311 records...")

    while True:

        params = BASE_PARAMS.copy()
        params["$limit"] = PAGE_SIZE
        params["$offset"] = offset

        response = requests.get(
            API_URL,
            params=params,
            timeout=120
        )

        response.raise_for_status()

        records = response.json()

        if not records:
            break

        all_records.extend(records)

        print(
            f"Fetched {len(records)} records | "
            f"Total: {len(all_records)}"
        )

        if len(records) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    return pd.DataFrame(all_records)


def main():

    df = fetch_all_records()

    if df.empty:
        raise ValueError("The API returned no records.")

    print(f"\nTotal records fetched: {len(df)}")

    engine = create_engine(DATABASE_URL)

    try:

        df.to_sql(
            name="311_service_requests",
            con=engine,
            schema="public",
            if_exists="replace",
            index=False,
            chunksize=2000
        )

        print("\nData loaded successfully!")
        print(f"Rows loaded: {len(df)}")
        print("PostgreSQL table: public.311_service_requests")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
