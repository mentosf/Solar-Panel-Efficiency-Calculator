import numpy as np
import pandas as pd
import pvlib


def add_gti(df: pd.DataFrame, lat: float, lon: float, tilt: float, azimuth: float) -> pd.DataFrame:
    """
    Обчислює GTI (Global Tilted Irradiance, Вт/м²) для довільного нахилу
    та азимуту панелі на основі GHI/DNI/DHI, отриманих з Open-Meteo,
    за допомогою моделі transposition з pvlib (isotropic).

    Це дозволяє змінювати кут нахилу/азимут прямо в інтерфейсі
    без повторних запитів до API.
    """
    df = df.copy()
    times = pd.DatetimeIndex(df["time"])

    ghi = pd.to_numeric(df["ghi"], errors="coerce").fillna(0.0).to_numpy(dtype="float64")
    dni = pd.to_numeric(df["dni"], errors="coerce").fillna(0.0).to_numpy(dtype="float64")
    dhi = pd.to_numeric(df["dhi"], errors="coerce").fillna(0.0).to_numpy(dtype="float64")

    solpos = pvlib.solarposition.get_solarposition(times, lat, lon)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=solpos["apparent_zenith"].to_numpy(dtype="float64"),
        solar_azimuth=solpos["azimuth"].to_numpy(dtype="float64"),
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        model="isotropic",
    )
    gti = pd.to_numeric(pd.Series(poa["poa_global"]), errors="coerce").fillna(0.0).to_numpy(dtype="float64")
    df["gti"] = np.clip(gti, 0, None)
    return df


def summarize_energy(df: pd.DataFrame, panel_area_m2: float = 1.0, panel_efficiency: float = 0.20) -> dict:
    """
    Рахує сумарну енергію (кВт·год), виходячи з GTI (Вт/м²) на погодинних
    даних: Вт/м² за 1 годину = Вт·год/м².
    """
    if df.empty:
        return {"total_kwh": 0.0, "avg_gti_w_m2": 0.0, "hours": 0}

    total_wh_per_m2 = df["gti"].sum()
    total_kwh = total_wh_per_m2 * panel_area_m2 * panel_efficiency / 1000
    return {
        "total_kwh": total_kwh,
        "avg_gti_w_m2": df["gti"].mean(),
        "hours": len(df),
    }