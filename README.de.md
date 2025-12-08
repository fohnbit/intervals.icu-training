# Intervals.icu Training Uploader & Coach Data Fetcher

Dieses Projekt besteht aus zwei Python-Programmen:

1. **`upload_plan_to_intervals.py`**  
   Lädt Trainingspläne aus JSON-Dateien in Intervals.icu hoch und aktualisiert bestehende Einträge automatisch.

2. **`fetch_weekly_coach_data.py`**  
   Ruft Wellness- und Trainingsdaten der letzten 7 Tage ab — ideal für adaptive Trainingssteuerung.

Alle Programme verwenden die gemeinsame Konfiguration `config.json`.

---

## Installation

Installiere die benötigten Python-Abhängigkeiten:

```bash
pip install -r requirements.txt
```

---

## Konfiguration

Bearbeite die Datei **`config.json`** und trage deine Daten ein:

```json
{
  "api_key": "DEIN_INTERVALS_API_KEY",
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

### Wichtig:

- `api_key`: Dein Intervals.icu API-Key  
- `athlete_id`: z. B. `i33675`  
- `plan_dir`: Ordner mit mehreren Trainingsdateien  
- `plan_file`: Alternative Einzeldatei  
- `default_start_time`: Uhrzeit, zu der Workouts angelegt werden  
- `weekly_output`: Datei für Wellness/Aktivitäten  

---

# Nutzung

---

## 1. Trainingspläne in Intervals.icu hochladen  
### Script: `upload_plan_to_intervals.py`

Das Script:

- lädt alle `.json`-Dateien im Trainingsordner  
- importiert nur Workouts **ab heutigem Datum**  
- erstellt neue Intervals-Events  
- aktualisiert bestehende Events anhand der `PLAN-ID`  
- erzeugt strukturierte Beschreibungseinträge:

```
[PLAN-ID:2026-02-04-SST-3x8]
- 15m ramp Z1 Free intensity=warmup
- 8m SS 90rpm intensity=active
- 5m Z1 Free intensity=recovery
- 8m SS 90rpm intensity=active
- 11m Z1 Free intensity=cooldown
```

### Beispiel-Trainingsdatei:

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

### Upload starten:

```bash
python3 upload_plan_to_intervals.py
```

---

## 2. Wellness- & Aktivitätsdaten der letzten 7 Tage abrufen  
### Script: `fetch_weekly_coach_data.py`

Das Script erzeugt eine Datei wie:

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

### Starten:

```bash
python3 fetch_weekly_coach_data.py
```

---

## Contributing

Pull Requests sind willkommen.  
Für größere Änderungen bitte zuerst ein Issue eröffnen.

---

## License

[MIT](https://choosealicense.com/licenses/mit/)
