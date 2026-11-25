
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler


# 1. Connect to PostgreSQL
load_dotenv()

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME")
)

engine = create_engine(connection_url)


# 2. Load ML features
query = """
SELECT *
FROM public.ml_features
ORDER BY request_date;
"""

df = pd.read_sql(query, engine)

print("Data loaded successfully!")
print("Dataset shape:", df.shape)


# 3. Select numerical features
features = [
    "total_requests",
    "invalid_date_records",
    "closed_missing_date_records",
    "invalid_date_percentage",
    "closed_missing_date_percentage"
]

X = df[features]


# 4. Isolation Forest
isolation_forest = IsolationForest(
    n_estimators=100,
    contamination=0.10,
    random_state=42
)

if_predictions = isolation_forest.fit_predict(X)

df["isolation_forest"] = pd.Series(if_predictions).map({
    1: "Normal",
    -1: "Anomaly"
})


# 5. Standardize features for LOF
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# 6. Local Outlier Factor
lof = LocalOutlierFactor(
    n_neighbors=5,
    contamination=0.10
)

lof_predictions = lof.fit_predict(X_scaled)

df["lof"] = pd.Series(lof_predictions).map({
    1: "Normal",
    -1: "Anomaly"
})


# 7. Compare model predictions
print("\nMODEL COMPARISON:")

print(
    df[[
        "request_date",
        "isolation_forest",
        "lof"
    ]].to_string(index=False)
)


# 8. Count anomalies detected by each model
print("\nANOMALY COUNTS:")

print(
    "Isolation Forest:",
    (df["isolation_forest"] == "Anomaly").sum()
)

print(
    "LOF:",
    (df["lof"] == "Anomaly").sum()
)


# 9. Show dates detected by both models
print("\nDATES FLAGGED BY BOTH MODELS:")

both_detected = df[
    (df["isolation_forest"] == "Anomaly") &
    (df["lof"] == "Anomaly")
]

print(
    both_detected[[
        "request_date",
        "total_requests",
        "invalid_date_records",
        "closed_missing_date_records",
        "invalid_date_percentage",
        "closed_missing_date_percentage"
    ]].to_string(index=False)
)


# 10. Show all detected anomalies
print("\nALL DETECTED ANOMALIES:")

anomalies = df[
    (df["isolation_forest"] == "Anomaly") |
    (df["lof"] == "Anomaly")
]

print(
    anomalies[[
        "request_date",
        "isolation_forest",
        "lof"
    ]].to_string(index=False)
)

# 11. Save detected anomalies to PostgreSQL without duplicates

anomaly_records = []

for _, row in df.iterrows():

    if row["isolation_forest"] == "Anomaly":
        anomaly_records.append({
            "request_date": row["request_date"],
            "model_name": "Isolation Forest",
            "anomaly_status": "Anomaly"
        })

    if row["lof"] == "Anomaly":
        anomaly_records.append({
            "request_date": row["request_date"],
            "model_name": "Local Outlier Factor",
            "anomaly_status": "Anomaly"
        })


# Remove previous predictions for the dates being processed
with engine.begin() as connection:
    connection.execute(text("""
        DELETE FROM public.anomaly_incidents
        WHERE request_date IN (
            SELECT request_date
            FROM public.ml_features
        )
        AND model_name IN (
            'Isolation Forest',
            'Local Outlier Factor'
        );
    """))


# Save the latest predictions
if anomaly_records:

    incidents_df = pd.DataFrame(anomaly_records)

    incidents_df.to_sql(
        "anomaly_incidents",
        engine,
        schema="public",
        if_exists="append",
        index=False
    )

    print("\nAnomaly incidents saved successfully!")

else:
    print("\nNo anomalies detected.")