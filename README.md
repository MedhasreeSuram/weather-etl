# Weather ETL Pipeline

This is a fun little Python ETL pipeline that extracts a year of daily weather data for four cities from a public API (Open-Meteo), cleans it and loads it into a relational SQLite database for analysis with SQL.

## Tech Stack

- **Python 3** (requests, pandas)
- **SQLite** (relational database)
- **Open-Meteo Historical Weather API** (free / no API key)

## How It Works

1. **Extract:** fetches daily max/min temperature and precipitation from the Open-Meteo API for each city.
2. **Transform:** renames columns, standardizes date formats, drops rows with missing temperatures and fills missing precipitation with 0.
3. **Load:** inserts the cleaned rows into SQLite. Loads are idempotent, so that means re-running the script updates existing rows instead of creating duplicates. I used a composite primary key on `(city, date)`.

Failures are logged per city, so one bad API call doesn't stop the whole run.

## Database Schema

**cities**

| Column    | Type | Notes       |
|-----------|------|-------------|
| city      | TEXT | Primary key |
| latitude  | REAL |             |
| longitude | REAL |             |

**daily_weather**

| Column     | Type | Notes                            |
|------------|------|----------------------------------|
| city       | TEXT | Foreign key to cities, part of PK |
| date       | TEXT | YYYY-MM-DD, part of PK           |
| temp_max_c | REAL | Daily high (°C)                  |
| temp_min_c | REAL | Daily low (°C)                   |
| precip_mm  | REAL | Total precipitation (mm)         |


## Example Queries

`queries.sql` includes more in-depth analysis such as:

- Hottest day per city (using `RANK()`)
- 7-day rolling average temperature
- Largest day-over-day temperature swings (using `LAG()`)
- Rainiest months per city

## Sample Findings

- Tokyo's hottest day in 2025 was 38.8 °C on 2025-08-30
- Atlanta's rainiest month was 2025-05 with 198.6 mm