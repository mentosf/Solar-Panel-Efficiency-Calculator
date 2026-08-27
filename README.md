# Solar Energy Assessment Tool for Ukraine

An interactive web application built with Streamlit for estimating solar radiation and potential solar panel energy generation across Ukraine. The application utilizes historical meteorological data from the Open-Meteo API, caches queries locally using SQLite, computes Global Tilted Irradiance (GTI) for custom panel orientations, and visualizes energy potential.

<img width="3728" height="1690" alt="image" src="https://github.com/user-attachments/assets/7114f0c1-6150-494f-b091-b776a68ad17c" />

## 📌 Features

- **Interactive Map Selection:** Pinpoint any geographic location across Ukraine using an interactive Folium map (`CartoDB Positron`).
- **Configurable Panel Parameters:** 
  - Panel Tilt Angle ($0^\circ$ to $90^\circ$).
  - Surface Azimuth ($0^\circ$ to $360^\circ$, North = $0^\circ$, East = $90^\circ$, South = $180^\circ$, West = $270^\circ$).
  - Panel Surface Area ($\text{m}^2$).
  - Panel Efficiency ($\%$).
- **Flexible Historical Date Range:** Select custom historical year ranges (from 1990 up to recent years).
- **Multi-granularity Analysis:** View multi-year averages or drill down into specific years and months.
- **Local SQLite Caching:** Automatic caching of hourly solar radiation values (GHI, DNI, DHI) to optimize API usage and enhance application speed.
- **Solar Energy Analytics:**
  - Total calculated energy output ($\text{kWh}$).
  - Average GTI ($\text{W/m}^2$).
  - Monthly energy production rankings and interactive charts.
  - Raw hourly radiation dataset preview.

---
<img width="3743" height="1778" alt="image" src="https://github.com/user-attachments/assets/20ea5040-9cc7-4a8d-9a42-2e61df4166cb" />

## 🏗️ Project Architecture

### Module Responsibilities

1. **`app.py`**: Controls the Streamlit layout, user input widgets, Folium map interaction, state management (`st.session_state`), triggers calculations, and renders charts and metrics.
2. **`extract.py`**: Manages data retrieval logic. Checks local SQLite cache for complete coverage of requested date ranges; if incomplete, fetches data from Open-Meteo API and persists it to cache.
3. **`db_cache.py`**: Encapsulates SQLite operations (`solar_cache.db`), database schema creation, indexing, querying, and bulk insertion of hourly radiation data.
4. **`solar_calc.py`**: Contains geometric solar radiation calculations to derive Global Tilted Irradiance (GTI) from Global Horizontal (GHI), Direct Normal (DNI), and Diffuse Horizontal (DHI) irradiance, and computes net energy generation.

---

## 🛠️ Tech Stack

- **Frontend & Dashboard:** Streamlit, Streamlit-Folium
- **Mapping & Geospatial:** Folium
- **Data Manipulation:** Pandas, NumPy
- **Database / Storage:** SQLite3
- **External API:** Open-Meteo Historical Weather API
- **HTTP Client:** Requests

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+ 
- `pip` (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/solar-energy-ukraine.git](https://github.com/your-username/solar-energy-ukraine.git)
   cd solar-energy-ukraine
