import requests
import pandas as pd
import streamlit as st
from db_cache import init_db, get_cached_data, save_to_cache
init_db()


def get_or_fetch_radiation(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Retrieves solar radiation data from local SQLite cache or fetches it from Open-Meteo API.

    First queries the local database. If the cached hourly records are sufficient
    to cover the requested date range, the cached data is returned. Otherwise,
    an HTTP request is made to the API, and the received data is saved to cache.

    Args:
        lat (float): Location latitude in decimal degrees.
        lon (float): Location longitude in decimal degrees.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: DataFrame containing ['time', 'ghi', 'dni', 'dhi',
        'year', 'month'] columns.
    """
    cached_df = get_cached_data(lat, lon, start_date, end_date)
    expected_hours = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days * 24 + 24
    if len(cached_df) >= expected_hours:
        return cached_df

    raw = fetch_radiation_history(lat, lon, start_date, end_date)
    if not raw.empty:
        save_to_cache(raw, lat, lon)

    return raw


ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def fetch_radiation_history(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetches hourly solar radiation data (GHI, DNI, DHI) from Open-Meteo Historical Weather API.

    Uses hourly averaged values (NOT "instant") as they represent energy (Wh/m²)
    received by a panel over that hour.
    GTI for arbitrary tilt/azimuth is calculated independently in solar_calc.py
    rather than fetched with fixed tilt/azimuth from API, allowing real-time angle
    adjustments in UI without redundant API calls.

    Results are cached via Streamlit for 24 hours.

    Args:
        lat (float): Geographic latitude.
        lon (float): Geographic longitude.
        start_date (str): Start date of period ('YYYY-MM-DD').
        end_date (str): End date of period ('YYYY-MM-DD').

    Returns:
        pd.DataFrame: Cleaned DataFrame with radiation time series and
        additional year/month fields.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "shortwave_radiation,direct_normal_irradiance,diffuse_radiation",
        "timezone": "auto",
    }
    resp = requests.get(ARCHIVE_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    hourly = data["hourly"]
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(hourly["time"]),
            "ghi": hourly["shortwave_radiation"],
            "dni": hourly["direct_normal_irradiance"],
            "dhi": hourly["diffuse_radiation"],
        }
    )

    for col in ("ghi", "dni", "dhi"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    return df