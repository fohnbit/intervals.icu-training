# 📘 Intervals.icu Coaching Helper  
### *Automatisiertes Trainings- & Wellnessdaten-Tool für Intervals.icu*

Dieses Projekt stellt eine modulare Python-Toolchain bereit, die:

- Trainings- und Wellnessdaten aus Intervals.icu abruft  
- individuelle Trainingspläne aus JSON lädt  
- Workouts strukturiert in Intervals.icu erstellt oder aktualisiert  
- Intervall-„Steps“ automatisch als lesbare Beschreibung in das Workout einfügt  
- eine Basis für datengetriebenes, adaptives Coaching bildet  

Das System ist ideal für Athleten, Coaches und Entwickler, die Intervals.icu automatisieren wollen.

---

## 🚀 Features

### 🟦 **Weekly Coach Data Fetcher (`fetch_weekly_coach_data.py`)**

Dieses Script holt für einen definierten Zeitraum:

- **Wellnessdaten:**  
  - CTL, ATL, Ramp Rate  
  - HRV  
  - Ruhepuls  
  - Schlafdauer, Schlafscore  
  - Gewicht  

- **Aktivitäten:**  
  - Dauer, Distanz, Höhenmeter  
  - NP, Durchschnittsleistung  
  - Herzfrequenz  
  - Training Load (TSS/TRIMP)  
  - Quelle (Garmin, Zwift, Concept2 …)

Ausgabe-Datei:  
```
weekly_coach_data.json
```

Diese dient als Grundlage für automatisierte Trainingsanpassung.

---

### 🟩 **Plan Upload Tool (`upload_plan_to_intervals.py`)**

Lädt geplante Workouts als Events in Intervals.icu und unterstützt:

- **Erstellen neuer Termine**
- **Überschreiben bestehender Termine durch PLAN-ID**
- automatische Beschreibung der Intervallstruktur im Format:

```
- 10m in Z2 (85rpm)
- 3m in Z5 (95rpm)
- 3m in Z2 (85rpm)
- 3m in Z5 (95rpm)
- 3m in Z2 (85rpm)
- 10m in Z1 (Free)
```

Trainingssteps werden **nicht** in `workout_doc.steps`, sondern in die **Description** geschrieben (bewährte Methode, funktioniert bei allen Athleten).

---

### 🟧 PLAN-ID Upsert System

Jedes Training erhält eine eindeutige ID:

```
[PLAN-ID:2025-12-08-SST-1]
```

Damit erkennt das Script:

- Event existiert → **Update (PUT)**
- Event existiert nicht → **Create (POST)**

So bleibt dein Kalender sauber und duplikatfrei.

---

## 📁 Projektstruktur

```
intervals-icu-coach/
 ├── config.json
 ├── config_loader.py
 ├── fetch_weekly_coach_data.py
 ├── upload_plan_to_intervals.py
 ├── trainings_plan.json
 ├── weekly_coach_data.json     # automatisch erzeugt
 └── README.md
```

---

## ⚙️ Installation

### Python installieren
macOS:
```
brew install python3
```

Linux:
```
sudo apt install python3 python3-pip
```

### Dependencies installieren
```
pip3 install requests
```

---

## 🔧 Konfiguration (`config.json`)

```json
{
  "api_key": "<DEIN_INTERVALS_API_KEY>",
  "athlete_id": "i12345",
  "base_url": "https://intervals.icu/api/v1",
  "default_start_time": "17:00:00",
  "paths": {
    "coach_data_file": "weekly_coach_data.json",
    "plan_file": "trainings_plan.json"
  }
}
```

---

## 📥 1. Coach-Daten abrufen

```
python3 fetch_weekly_coach_data.py
```

Dies erzeugt die Datei:

```
weekly_coach_data.json
```

mit Wellness- und Aktivitätsdaten, z. B.:

```json
{
  "date": "2025-12-05",
  "wellness": {
    "ctl": 25.9,
    "atl": 30.4,
    "hrv": 49,
    "resting_hr": 47,
    "sleep_hours": 7.2
  },
  "activities": [
    {
      "type": "Ride",
      "duration_s": 4525,
      "training_load": 81
    }
  ]
}
```

---

## 📝 2. Trainingsplan definieren (`trainings_plan.json`)

```json
[
  {
    "plan_id": "2025-12-08-VO2-1",
    "date": "2025-12-08",
    "sport": "Ride",
    "name": "Bike - VO2 Max Intervals",
    "duration_minutes": 32,
    "steps": [
      {"duration": "10m", "zone": "Z2", "cadence": "85rpm"},
      {"duration": "3m", "zone": "Z5", "cadence": "95rpm"},
      {"duration": "3m", "zone": "Z2", "cadence": "85rpm"},
      {"duration": "3m", "zone": "Z5", "cadence": "95rpm"},
      {"duration": "3m", "zone": "Z2", "cadence": "85rpm"},
      {"duration": "10m", "zone": "Z1", "cadence": "Free"}
    ]
  }
]
```

---

## 📤 3. Trainingsplan nach Intervals.icu hochladen

```
python3 upload_plan_to_intervals.py
```

Das Script:

- prüft bestehende Events
- liest PLAN-ID aus der Beschreibung
- erstellt oder aktualisiert
- fügt strukturierte Steps hinzu

Ergebnis in Intervals.icu:

```
[PLAN-ID:2025-12-08-VO2-1]
- 10m in Z2 (85rpm)
- 3m in Z5 (95rpm)
...
```

---

## 🧠 Erweiterungen (optional)

### Adaptives Coaching
Auf Basis von `weekly_coach_data.json` können Regeln implementiert werden:

- **HRV niedrig → Intensität reduzieren**
- **ATL hoch → Recovery Ride**
- **Schlaf < 6h → Training kürzen**
- **RPE > 8 zuletzt → nächste Woche leichter**

### Automatische Planerstellung
Ein Beispiel `plan_generator.py` könnte:

- Wochen-TSS planen  
- Periodisierung einbauen  
- GA1/GA2/SST/VO2-Blockstrukturen generieren  
- Höhenmeter berücksichtigen  

---

## 🤝 Mitwirken

Pull Requests sind willkommen!  
Das Projekt ist klar strukturiert und einfach erweiterbar.

---

## 📄 Lizenz

MIT License — freie Nutzung & Weiterentwicklung erlaubt.
