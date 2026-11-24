
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

env = os.environ.copy()
env["PGPASSWORD"] = os.getenv("DB_PASSWORD", "")

psql = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"

sql_files = [
    "clean_data.sql",
    "daily_metrics.sql"
]

for filename in sql_files:
    sql_path = BASE_DIR / "sql" / filename

    print(f"\nRunning {filename}...")

    subprocess.run(
        [
            psql,
            "-h", os.getenv("DB_HOST", "localhost"),
            "-p", os.getenv("DB_PORT", "5432"),
            "-U", os.getenv("DB_USER", "postgres"),
            "-d", os.getenv("DB_NAME", "anomark"),
            "-v", "ON_ERROR_STOP=1",
            "-f", str(sql_path)
        ],
        env=env,
        check=True
    )

    print(f"Completed: {filename}")

print("\nAnomark pipeline completed successfully!")