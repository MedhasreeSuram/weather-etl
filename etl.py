import logging
import sqlite3

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

API_URL = "https://archive-api.open-meteo.com/v1/archive"
DB_PATH = "weather.db"
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CITIES = {
    "Atlanta": (33.749, -84.388),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
}

def extract(lat, lon):
    #fetch daily weather JSON from the Open-Meteo API
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def transform(city, raw):
    #clean the JSON into a clean dataframe
    df = pd.DataFrame(raw["daily"])
    df = df.rename(columns={
        "time": "date",
        "temperature_2m_max": "temp_max_c",
        "temperature_2m_min": "temp_min_c",
        "precipitation_sum": "precip_mm",
    })
    df["city"] = city
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["temp_max_c", "temp_min_c"])
    df["precip_mm"] = df["precip_mm"].fillna(0)
    return df[["city", "date", "temp_max_c", "temp_min_c", "precip_mm"]]

def init_db(conn):
    #create the tables if they don't exist (first time)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cities (
        cities TEXT PRIMARY KEY,
        latitude REAL,
        longitude REAL
    )""")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_weather (
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        temp_max_c REAL,
        temp_min_c REAL,
        precip_mm REAL,
        PRIMARY KEY (city, date),
        FOREIGN KEY (city) REFERENCES cities(city)
    )""")

def load(conn, city, lat, lon, df):
    #insert the data.. rerunning should not create duplicates
    conn.execute("INSERT OR IGNORE INTO cities VALUES (?,?,?)", (city, lat, lon))
    rows = list(df.itertuples(index=False, name=None))
    conn.executemany("INSERT OR REPLACE INTO daily_weather VALUES (?,?,?,?,?)", rows)
    conn.commit()
    return len(rows)

def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    for city, (lat, lon) in CITIES.items():
        try:
            logging.info("Extracting %s", city)
            raw = extract(lat,lon)
            df = transform(city, raw)
            n = load(conn, city, lat, lon, df)
            logging.info("Loaded %d rows for %s", n, city)
        except Exception:
            logging.exception("Failed for %s", city)
    conn.close()

if __name__ == "__main__":
    main()