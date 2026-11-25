import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

query = """
SELECT *
FROM public.daily_quality_summary
ORDER BY request_date;
"""

df = pd.read_sql(query, engine)
engine.dispose()

print("\nDaily quality data loaded successfully!")
print("Shape:", df.shape)
print(df.head())