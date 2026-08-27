from datetime import date

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from extract import get_or_fetch_radiation
from solar_calc import add_gti, summarize_energy

st.set_page_config(page_title="Сонячна енергія по Україні", layout="wide")
st.title("☀️ Оцінка сонячної енергії для панелей в Україні")

MONTHS_UA = [
    "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень",
]

# ---------------- Сайдбар: параметри панелі ----------------
st.sidebar.header("Параметри панелі")
tilt = st.sidebar.slider("Нахил панелі, °", 0, 90, 30)
azimuth = st.sidebar.slider(
    "Азимут, ° (0=Північ, 90=Схід, 180=Південь, 270=Захід)", 0, 360, 180
)
panel_area = st.sidebar.number_input("Площа панелі, м²", min_value=0.1, value=1.0, step=0.1)
panel_eff = st.sidebar.slider("ККД панелі, %", 5, 30, 20) / 100

st.sidebar.header("Період даних (архів)")
this_year = date.today().year
start_year = st.sidebar.number_input(
    "Рік початку", min_value=1990, max_value=this_year, value=this_year - 6
)
end_year = st.sidebar.number_input(
    "Рік кінця", min_value=1990, max_value=this_year, value=this_year - 1
)

year_mode = st.sidebar.radio("Рік для відображення", ["Середнє за роки", "Конкретний рік"])
selected_year = None
if year_mode == "Конкретний рік":
    selected_year = st.sidebar.selectbox("Оберіть рік", list(range(start_year, end_year + 1))[::-1])

month_mode = st.sidebar.radio("Місяць для відображення", ["Середнє за місяцями (весь рік)", "Конкретний місяць"])
selected_month = None
if month_mode == "Конкретний місяць":
    selected_month = st.sidebar.selectbox(
        "Оберіть місяць", list(range(1, 13)), format_func=lambda m: MONTHS_UA[m - 1]
    )

st.sidebar.markdown("---")


# ---------------- Карта ----------------
st.subheader("1. Оберіть точку на карті України")

if "point" not in st.session_state:
    st.session_state.point = {"lat": 49.0, "lon": 31.0}

m = folium.Map(location=[49.0, 31.0], zoom_start=6, tiles="CartoDB positron")
folium.Marker(
    [st.session_state.point["lat"], st.session_state.point["lon"]],
    tooltip="Обрана точка",
).add_to(m)

map_data = st_folium(m, height=480, width=None, key="ua_map")

if map_data and map_data.get("last_clicked"):
    new_lat = map_data["last_clicked"]["lat"]
    new_lon = map_data["last_clicked"]["lng"]
    if (new_lat, new_lon) != (st.session_state.point["lat"], st.session_state.point["lon"]):
        st.session_state.point["lat"] = new_lat
        st.session_state.point["lon"] = new_lon
        st.rerun()

lat = st.session_state.point["lat"]
lon = st.session_state.point["lon"]
st.write(f"📍 Обрана точка: **{lat:.4f}, {lon:.4f}**")

# ---------------- Розрахунок ----------------
st.subheader("2. Розрахунок")

if st.button("Розрахувати", type="primary"):
    with st.spinner("Завантажуємо дані з Open-Meteo та рахуємо GTI..."):
        raw = get_or_fetch_radiation(lat, lon, f"{start_year}-01-01", f"{end_year}-12-31")
        if raw.empty:
            st.error("Не вдалося отримати дані для цієї точки/періоду.")
            st.stop()
        full = add_gti(raw, lat, lon, tilt, azimuth)

    filtered = full.copy()
    if selected_year is not None:
        filtered = filtered[filtered["year"] == selected_year]
    if selected_month is not None:
        filtered = filtered[filtered["month"] == selected_month]

    if filtered.empty:
        st.warning("Немає даних для обраного періоду.")
    else:
        n_years = filtered["year"].nunique()
        result = summarize_energy(filtered, panel_area, panel_eff)

        col1, col2, col3 = st.columns(3)
        label = "Сумарна енергія за період" if selected_year is not None else "Сер. сумарна енергія за рік"
        value = result["total_kwh"] if selected_year is not None else result["total_kwh"] / max(n_years, 1)
        col1.metric(label, f"{value:.1f} кВт·год")
        col2.metric("Середня радіація на панель", f"{result['avg_gti_w_m2']:.0f} Вт/м²")
        col3.metric("Годин з даними", result["hours"])

        st.markdown("### Порівняння по місяцях (для пошуку найвигіднішого місяця)")
        base = full[full["year"] == selected_year] if selected_year is not None else full

        def _monthly_kwh(g: pd.DataFrame) -> float:
            e = summarize_energy(g, panel_area, panel_eff)["total_kwh"]
            years_in_group = g["year"].nunique() or 1
            return e / years_in_group

        monthly = base.groupby("month").apply(_monthly_kwh).reindex(range(1, 13)).fillna(0)
        chart_df = pd.DataFrame(
            {
                "Місяць": [MONTHS_UA[m - 1] for m in monthly.index],
                "Енергія, кВт·год": monthly.values
            }
        ).sort_values(by="Енергія, кВт·год", ascending=False)
        chart_df["Місяць"] = pd.Categorical(
            chart_df["Місяць"],
            categories=chart_df["Місяць"],
            ordered=True
        )

        st.bar_chart(chart_df.set_index("Місяць"))

        with st.expander("Показати погодинні дані"):
            st.dataframe(filtered[["time", "ghi", "dni", "dhi", "gti"]])


else:
    st.info("Натисніть «Розрахувати», щоб завантажити дані та побачити результат.")