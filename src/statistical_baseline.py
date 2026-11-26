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

print("\nAvailable columns:")
print(df.columns.tolist())

print("\nStatistical summary:")
print(df.describe())


# --------------------------------
# Statistical Anomaly Detection
# --------------------------------

metrics = [
    "invalid_date_percentage",
    "closed_missing_date_percentage"
]

for metric in metrics:

    mean_value = df[metric].mean()
    std_value = df[metric].std()

    df[f"{metric}_zscore"] = (
        df[metric] - mean_value
    ) / std_value

    df[f"{metric}_anomaly"] = (
        df[f"{metric}_zscore"].abs() > 3
    )

print("\nAnomaly Detection Results:")

for metric in metrics:
    print(f"\nResults for {metric}:")

    print(
        df[
            [
                "request_date",
                metric,
                f"{metric}_zscore",
                f"{metric}_anomaly"
            ]
        ].to_string(index=False)
    )


# --------------------------------
# Statistical Anomaly Detection
# --------------------------------

metrics = [
    "invalid_date_percentage",
    "closed_missing_date_percentage"
]

for metric in metrics:

    mean_value = df[metric].mean()
    std_value = df[metric].std()

    df[f"{metric}_zscore"] = (
        df[metric] - mean_value
    ) / std_value

    df[f"{metric}_anomaly"] = (
        df[f"{metric}_zscore"].abs() > 3
    )

print("\nAnomaly Detection Results:")

for metric in metrics:
    print(f"\nResults for {metric}:")

    print(
        df[
            [
                "request_date",
                metric,
                f"{metric}_zscore",
                f"{metric}_anomaly"
            ]
        ].to_string(index=False)
    )



# --------------------------------
# Save Anomaly Results to PostgreSQL
# --------------------------------

results_engine = create_engine(DATABASE_URL)

try:
    df.to_sql(
        name="statistical_anomaly_results",
        con=results_engine,
        schema="public",
        if_exists="replace",
        index=False
    )
    print("\nAnomaly results saved to PostgreSQL!")
finally:
    results_engine.dispose()











