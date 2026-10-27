import requests

url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

params = {
    "$limit": 5,
    "$select": "unique_key,created_date,complaint_type,borough"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

records = response.json()

print("NYC 311 API connection successful!")
print("Records fetched:", len(records))

for record in records:
    print(record)