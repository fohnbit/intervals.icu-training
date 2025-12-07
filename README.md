🚀 Quick Start Guide – Intervals.icu Trainings-Upload System

Dieses Projekt ermöglicht es, Trainingspläne als JSON-Dateien automatisch in Intervals.icu hochzuladen, inklusive Struktur, Zonen, Kadenzen, Warmup/Ramp, Intensität usw.
Es unterstützt zudem mehrere Trainingsdateien im Verzeichnis, automatisches Updaten existierender Events und ignoriert vergangene Workouts.

⸻

1️⃣ Repository klonen

git clone <URL>
cd intervals.icu-training


⸻

2️⃣ Python-Umgebung vorbereiten

macOS

pip3 install -r requirements.txt

Windows / Linux

pip install -r requirements.txt


⸻

3️⃣ config.json einrichten

Öffne die Datei:

config.json

Hier müssen drei wichtige Dinge gesetzt werden:

⸻

🔐 API-Daten

Trage deine Intervals.icu Benutzer-Daten ein:

"api_key": "DEIN_INTERVALS_API_KEY",
"athlete_id": "iDEINE_ID",
"base_url": "https://intervals.icu/api/v1",

👉 API-Key findest du in Intervals.icu
→ Settings → API Key

👉 athlete_id findest du in der URL, z. B.:
https://intervals.icu/athlete/i33775 → i33775

⸻

📁 Trainingsdateien

Ein Verzeichnis mit vielen Trainingsdateien verwenden

Empfohlenes Setup:

"paths": {
    "plan_dir": "training_plans/"
}

Alle .json Trainingsdateien in training_plans/ werden automatisch geladen.

⸻

🕒 Startzeit für Workouts festlegen

(default: 17:00 Uhr)

"default_start_time": "17:00:00"


⸻

4️⃣ Trainings im JSON-Format anlegen

Beispiel:

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

💡 Alle Schritte werden automatisch in eine Intervals-kompatible Description umgewandelt:

[PLAN-ID:2026-02-04-SST-3x8]
- 15m ramp Z1 Free intensity=warmup
- 8m SS 90rpm intensity=active
- 5m Z1 Free intensity=recovery
...


⸻

5️⃣ Script zum Hochladen ausführen

python3 upload_plan_to_intervals.py

Das Script:
	•	lädt alle Trainings ab heutigem Datum
	•	gleicht anhand der PLAN-ID ab
	•	aktualisiert existierende Workouts
	•	erstellt neue Workouts via Bulk-Upload
	•	zeigt Fehler und gesendete Daten sauber an

⸻

6️⃣ Erfolg prüfen in Intervals.icu

Navigation:

→ Calendar → Training

Dort siehst du:
	•	Titel
	•	Description (inkl. Steps, Ramp, Intensität)
	•	Startzeit
	•	Struktur

⸻

7️⃣ Typische Fehler & Lösungen

❌ 422 „Invalid Type“

→ "sport" falsch geschrieben.
Erlaubte Werte:
	•	"Ride"
	•	"Run"
	•	"VirtualRow"
	•	"Strength" / "WeightTraining"

❌ Kein Event wird aktualisiert

→ plan_id muss eindeutig sein
→ und im Description-Feld der Events stehen.

❌ Keine Steps sichtbar

→ Intervals zeigt Steps nicht immer an
→ wichtig: Die Description wird verwendet
→ Steps im Payload trotzdem beibehalten (zukunftssicher).

⸻

📊 fetch_weekly_coach_data.py – Wozu dient dieses Script?

Dieses Script holt alle relevanten Trainings- und Wellnessdaten der letzten 7 Tage aus Intervals.icu, und zwar kombiniert in einem einzigen strukturierten JSON, das perfekt geeignet ist, um:
	•	deine Trainingsbelastung (CTL, ATL, RampRate)
	•	Erholung (HRV, restingHR, Schlaf)
	•	dein Gewicht
	•	alle durchgeführten Aktivitäten (inkl. Power, HR, TL, NP, etc.)

automatisch auszuwerten.

Damit kann dein Coach-Script (oder ChatGPT) jederzeit wissen:
	•	wie fit/ermüdet du bist
	•	wie viel Trainingsstress du hattest
	•	ob Intensitäten angepasst werden müssen
	•	ob du überlastet oder unterfordert bist

🔍 Was genau holt das Script?

Für jeden Tag:

Wellness-Daten:
	•	CTL / ATL / RampRate
	•	Gewicht
	•	Ruhepuls
	•	HRV
	•	Schlafdauer + Schlafscore
	•	Aktualisierungszeit

Trainings pro Tag:
	•	Trainingsart (Ride, Strength, Rowing…)
	•	Dauer (moving_time)
	•	Distanz
	•	Höhenmeter
	•	NP (normalized power)
	•	Avg HR / Max HR
	•	Training Load (TL / TSS)
	•	Strain Score
	•	Device Name (Garmin, C2, etc.)

📂 Ausgabeformat

Das Script erzeugt eine Datei:

weekly_data.json

Beispielstruktur:

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
        "avg_hr": 130,
        "max_hr": 165
      }
  ]
}

🎯 Wofür ist das nützlich?
	•	Adaptive Trainingssteuerung (z. B. GPT entscheidet über RPE, Wattvorgaben)
	•	Erholung überwachen (HRV/RestingHR/CTL/ATL)
	•	Automatisierte Plan-Anpassung
	•	Verhindert Überlastung
	•	Objektive Leistungsentwicklung

