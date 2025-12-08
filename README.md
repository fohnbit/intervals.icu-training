# Intervals.icu Training Uploader & Coach Data Fetcher

**Languages:** English | [Deutsch](README.de.md)

This project contains two Python programs:

1. **`upload_plan_to_intervals.py`**  
   Uploads training plans from JSON files to Intervals.icu and automatically updates existing entries.

2. **`fetch_weekly_coach_data.py`**  
   Fetches wellness and training data from the last 7 days — ideal for adaptive training guidance.

Both programs use the shared configuration file `config.json`.

---

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
