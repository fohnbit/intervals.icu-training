# Intervals.icu Training Uploader & Coach Data Fetcher

**Languages:** English | [Deutsch](README.de.md)

This project contains two Python programs:

1. **`upload_plan_to_intervals.py`**  
   Uploads training plans from JSON files to Intervals.icu and automatically updates existing entries.

2. **`fetch_weekly_coach_data.py`**  
   Fetches wellness and training data from the last 7 days — ideal for adaptive training guidance.

Both programs use the shared configuration file `config.json`.

---

## Quickinstalltion

## macOS (Terminal / zsh / bash)

```bash
git --version
python3 --version || brew install python
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/fohnbit/intervals.icu-training.git
cd intervals.icu-training
mv config.json.default config.json
nano config.json
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python3 weekly_coach_data.py
```

## Windows (Powershell)

```powershell
# -------------------------------------------
# Check if Git is installed
# Prüfen ob Git installiert ist
git --version

# Check if Python is installed
# Prüfen ob Python installiert ist
python --version

# If Python is missing, install from:
# Falls Python fehlt, installieren von:
# https://www.python.org/downloads/windows/
# IMPORTANT: Enable "Add Python to PATH" during installation
# WICHTIG: Beim Installieren "Add Python to PATH" aktivieren!

# -------------------------------------------
# Create project folder
# Projektordner anlegen
mkdir C:\projects
cd C:\projects

# -------------------------------------------
# Clone the repository
# Repository klonen
git clone https://github.com/fohnbit/intervals.icu-training.git
cd intervals.icu-training

# -------------------------------------------
# Copy and edit configuration file
# Beispiel-Config übernehmen und bearbeiten
mv config.json.default config.json

# Open config.json for editing
# config.json zum Bearbeiten öffnen
notepad config.json

# -------------------------------------------
# Create Python virtual environment
# Virtuelle Python-Umgebung erstellen
python -m venv venv

# If PowerShell blocks script execution:
# Falls PowerShell die Ausführung blockiert:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate venv
# venv aktivieren
.\venv\Scripts\Activate.ps1

# -------------------------------------------
# Upgrade pip
# pip aktualisieren
pip install --upgrade pip

# Install required dependencies
# Benötigte Abhängigkeiten installieren
pip install -r requirements.txt

# -------------------------------------------
# First script execution (default: last 7 days)
# Erstes Ausführen (Standard: letzte 7 Tage)
python weekly_coach_data.py
```

## Installation

Install all required Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Edit **`config.json`** and add your Intervals.icu details:

```json
{
  "api_key": "YOUR_INTERVALS_API_KEY",
  "athlete_id": "i12345",
  "base_url": "https://intervals.icu/api/v1",

  "default_start_time": "17:00:00",

  "paths": {
    "plan_dir": "training_plans/",
    "plan_file": null,
    "weekly_output": "weekly_data.json"
  }
}
```

### Important

- `api_key`: your Intervals.icu API key  
- `athlete_id`: e.g. `i33675`  
- `plan_dir`: folder containing multiple training plan files  
- `plan_file`: alternative single file  
- `default_start_time`: default start time for newly created workouts  
- `weekly_output`: output file for wellness/activity data  

---

# Usage

---

## 1. Upload training plans to Intervals.icu  
### Script: `upload_plan_to_intervals.py`

This script:

- loads all `.json` files inside the training directory  
- imports only workouts **from today onward**  
- creates new Intervals.icu events  
- updates existing events using their `PLAN-ID`  
- generates structured descriptions:

```
[PLAN-ID:2026-02-04-SST-3x8]
- 15m ramp Z1 Free intensity=warmup
- 8m SS 90rpm intensity=active
- 5m Z1 Free intensity=recovery
- 8m SS 90rpm intensity=active
- 11m Z1 Free intensity=cooldown
```

### Example training file:

```json
[
  {
    "date": "2026-02-04",
    "plan_id": "2026-02-04-SST-3x8",
    "name": "Sweetspot 3×8min",
    "sport": "Ride",
    "category": "WORKOUT",
    "steps": [
      { "duration": "15m", "zone": "Z1", "cadence": "Free", "intensity": "warmup", "ramp": true },
      { "duration": "8m",  "zone": "SS", "cadence": "90rpm", "intensity": "active" },
      { "duration": "5m",  "zone": "Z1", "cadence": "Free", "intensity": "recovery" }
    ]
  }
]
```

### Run the upload:

```bash
python3 upload_plan_to_intervals.py
```

---

## 2. Fetch last 7 days of wellness & activity data  
### Script: `fetch_weekly_coach_data.py`

The script generates output such as:

```json
{
  "date": "2025-12-05",
  "wellness": {
    "ctl": 25.9,
    "atl": 30.4,
    "weight": 71.3,
    "resting_hr": 47,
    "hrv": 49,
    "sleep_hours": 7.2
  },
  "activities": [
    {
      "type": "Ride",
      "duration_s": 4525,
      "training_load": 81,
      "np_est": 178,
      "avg_hr": 130
    }
  ]
}
```

### Run the script:

```bash
python3 fetch_weekly_coach_data.py
```

---

## Contributing

Pull requests are welcome.  
For larger changes, please open an issue first.

---

## License

[MIT](https://choosealicense.com/licenses/mit/)
