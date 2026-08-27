import sqlite3
import pandas as pd

DB_FILE = "solar_cache.db"

def init_db():
    """Initializes SQLite database and required tables for radiation caching.

        Creates the `radiation_cache` table (with primary key on lat, lon, time)
        and composite index `idx_coords_time` for fast querying by location
        and date ranges.
        """
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS radiation_cache (
                lat REAL,
                lon REAL,
                time TEXT,
                ghi REAL,
                dni REAL,
                dhi REAL,
                PRIMARY KEY (lat, lon, time)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_coords_time 
            ON radiation_cache (lat, lon, time)
        """)

def get_cached_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Retrieves cached solar radiation data from local SQLite database.

    Rounds coordinates to 3 decimal places to prevent floating-point precision issues.
    Constructs time bounds covering 00:00 of start_date to 23:00 of end_date.

    Args:
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.
        start_date (str): Start date ('YYYY-MM-DD').
        end_date (str): End date ('YYYY-MM-DD').

    Returns:
        pd.DataFrame: DataFrame containing retrieved cached records.
        Returns an empty DataFrame if no data exists.
    """
    lat_round = round(lat, 3)
    lon_round = round(lon, 3)

    start_time = f"{start_date} 00:00:00"
    end_time = f"{end_date} 23:00:00"

    query = """
        SELECT time, ghi, dni, dhi 
        FROM radiation_cache 
        WHERE lat = ? AND lon = ? AND time BETWEEN ? AND ?
        ORDER BY time ASC
    """
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(query, conn, params=(lat_round, lon_round, start_time, end_time))

    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])
        df["year"] = df["time"].dt.year
        df["month"] = df["time"].dt.month
    return df

def save_to_cache(df: pd.DataFrame, lat: float, lon: float):
    """Saves API-fetched solar radiation data to the SQLite database.

        Attaches rounded coordinates (3 decimal places) to each record, converts
        timestamps to ISO string format, and inserts data into table.
        Primary key conflicts `(lat, lon, time)` are ignored (`INSERT OR IGNORE`).

        Args:
            df (pd.DataFrame): DataFrame containing API data with columns
                ['time', 'ghi', 'dni', 'dhi'].
            lat (float): Latitude coordinate.
            lon (float): Longitude coordinate.
        """
    if df.empty:
        return

    df_save = df.copy()
    df_save["lat"] = round(lat, 3)
    df_save["lon"] = round(lon, 3)
    df_save["time"] = df_save["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    records = df_save[["lat", "lon", "time", "ghi", "dni", "dhi"]].to_records(index=False)

    with sqlite3.connect(DB_FILE) as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO radiation_cache (lat, lon, time, ghi, dni, dhi)
            VALUES (?, ?, ?, ?, ?, ?)
        """, records)