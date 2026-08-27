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

## 🚀 Installation & Setup Guide

Follow these step-by-step instructions to get the project up and running on your local machine.

### Prerequisites

Ensure you have **Python 3.9** or higher installed on your system. You can verify your Python version by running:

```bash
python --version
```

---

### Step 1: Clone the Repository

Clone the project repository from GitHub to your local system and navigate to the project directory:

```bash
git clone [https://github.com/mentosf/project-name.git](https://github.com/mentosf/project-name.git)
cd solar-energy-ukraine
```

---

### Step 2: Create a Virtual Environment

It is strongly recommended to set up an isolated virtual environment to manage dependencies properly:

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **On Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

*Note: You will know your environment is active when `(venv)` appears at the beginning of your terminal prompt.*

---

### Step 3: Install Required Dependencies

Ensure `pip` is updated to the latest version and install all required modules using `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Run the Application

Once all packages are successfully installed, launch the Streamlit application by running:

```bash
streamlit run app.py
```

The application will automatically start and open in your default web browser at:
`http://localhost:8501`

---

### 🗄️ Database Initialization Note

The local database (`solar_cache.db`) is automatically initialized upon application startup. You do not need to run any manual database migrations or schema creation scripts.

---

## 📊 How to Use the Application

1. **Select Location:** Click on any point on the map of Ukraine to automatically set the latitude and longitude.
2. **Adjust Parameters (Sidebar):**
   - Choose tilt angle and panel orientation (azimuth).
   - Enter your panel's surface area and nominal efficiency rating.
   - Select the historical year range (e.g., last 5 years).
3. **Run Simulation:** Click the **"Розрахувати"** (Calculate) button.
   - The app will retrieve weather data from the local SQLite cache or request it from the Open-Meteo API.
   - The model will convert raw solar radiation into total generated kilowatt-hours ($\text{kWh}$).
4. **Analyze Results:** Explore overall metrics, monthly energy production bar charts, and detailed hourly data tables.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
