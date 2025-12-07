📘 README – Intervals.icu Trainingsplan Automatisierung

Dieses Projekt bietet ein vollständiges Framework, um Trainingspläne automatisch in Intervals.icu zu laden, zu aktualisieren und mit Coaching-Daten abzugleichen.

Es besteht aus:
	1.	Upload-System für Trainingspläne
	2.	Automatischem Fetch der letzten Woche (Wellness + Aktivitäten)
	3.	Eigenem Trainingsformat (.json), das beliebig erweitert werden kann
	4.	Fehlerfreier Upsert-Logik
	5.	Zonen- und Kadenzen-Parsing für Intervals.icu
	6.	PLAN-ID Matching zur sicheren Aktualisierung

⸻

🗂 Projektstruktur

intervals.icu-training/
│
├── config.json
├── upload_plan_to_intervals.py
├── fetch_weekly_coach_data.py
├── config_loader.py
│
└── trainings/
    ├── februar_2026.json
    ├── maerz_2026_intervals_plan_v2.json
    └── weitere_pläne.json

Alle Trainingspläne im Ordner trainings/ werden geladen.

⸻

⚙️ 1. Installation

Python-Abhängigkeiten installieren

pip3 install requests


⸻

🔑 2. config.json

Beispiel:

{
  "api_key": "DEIN_API_KEY",
  "athlete_id": "XXXXXX",
  "base_url": "https://intervals.icu/api/v1",
  "default_start_time": "17:00:00",

  "paths": {
    "training_dir": "trainings"
  }
}


⸻

🧠 3. Trainingsplan-Format

Eine Trainingsdatei besteht aus einem Array von Workouts:

[
  {
    "date": "2026-03-06",
    "plan_id": "2026-03-06-VO2-5x3",
    "name": "VO2max 5×3min",
    "type": "Ride",
    "moving_time": 4500,
    "steps": [
      { "duration": "15m", "zone": "Z1", "cadence": "Free", "description": "Aufwärmen" },
      { "duration": "3m",  "zone": "Z5", "cadence": "95-100rpm", "description": "Intervall 1 VO2max" },
      { "duration": "3m",  "zone": "Z1", "cadence": "Free", "description": "Pause 1 locker" }
    ]
  }
]

✔ Unterstützte Felder:

Feld	Bedeutung
date	ISO Datum
plan_id	Eindeutige ID zur Wiedererkennung
type	Ride, Strength, VirtualRow, Run
moving_time	Dauer in Sekunden
steps	Liste mit Intervall-Schritten
zone	z. B. Z1, Z2, Z3, Z5, SS
cadence	Zahl, Bereich („90-100rpm“), text („Free“)


⸻

🆙 4. Upload-System (Upsert)

Das Script:

→ lädt alle .json aus trainings/

→ filtert alle Trainings ab heute

→ lädt sie hoch oder aktualisiert sie

(Matching über [PLAN-ID:xxxxxx] in der Beschreibung)

⸻

🧾 4.1 upload_plan_to_intervals.py

Funktionen:
	•	Liest ALLE Trainingspläne automatisch
	•	Erkennt bestehende Events über PLAN-ID
	•	Erstellt neue Events (bulk upload)
	•	Aktualisiert vorhandene Events (PUT)
	•	Schreibt Steps sauber in die Description:

Beispiel:

[PLAN-ID:2026-03-06-VO2-5x3]
- 15m in Z1 Free
- 3m in Z5 95-100rpm
- 3m in Z1 Free
...

Unterstützte Sportarten:

Eingabe	Intervals-Typ
Ride	Ride
Strength / Kraft	WeightTraining
VirtualRow	VirtualRow
Lauf	Run


⸻

🔍 5. Wellness + Aktivitäten abrufen

Die API liefert:
	•	Training Load (CTL, ATL, RampRate)
	•	Gewicht
	•	Ruhepuls
	•	HRV
	•	Schlafdauer + Schlafscore
	•	Aktivitäten (inkl. NP, HR, TL, Device)

Script: fetch_weekly_coach_data.py

Ausgabe-Schema:

[
  {
    "date": "2025-12-05",
    "wellness": {
      "ctl": 25.91,
      "atl": 30.46,
      "rampRate": 0.65,
      "weight": 71.3,
      "resting_hr": 47,
      "hrv": 49,
      "sleep_hours": 7.2
    },
    "activities": [
      {
        "id": "i110338643",
        "name": "Krafttraining",
        "type": "WeightTraining",
        "avg_hr": 110,
        "moving_s": 2663,
        "np_est": null
      }
    ]
  }
]

Dieses Dataset dient als Grundlage für:
	•	automatische Trainingsanpassung
	•	Belastungssteuerung
	•	Tagesform-Erkennung

⸻

🧪 6. Upsert-Logik

Wenn Event vorhanden:

→ PUT /events/{id}

Wenn nicht vorhanden:

→ Bulk-Upload via POST:

POST /events/bulk


⸻

🏷 PLAN-ID Matching

In jeder Beschreibung steht:

[PLAN-ID:2026-03-06-VO2-5x3]

Der Algorithmus:
	1.	Alle Events im Zeitraum abrufen
	2.	PLAN-ID extrahieren
	3.	Exakt matchen
	4.	Update statt Doppelung

Damit passiert nie, dass Trainings doppelt erzeugt werden.

⸻

📥 7. Schritte-Format (Description)

Wird automatisch generiert:

- 10m in Z2 85rpm
- 3m in Z5 95-100rpm
- 3m in Z2 Free

Kein Klammernformat, Intervals.icu-kompatibel.

⸻

📤 8. Lade Trainings hoch

Einfach:

python3 upload_plan_to_intervals.py


⸻

📅 9. Neue Trainings hinzufügen

.json ins trainings/ Verzeichnis legen.

Der Upload erkennt automatisch:
	•	nur zukünftige Einheiten
	•	PLAN-ID Matching
	•	Upsert

⸻

📌 10. Bekannte Einschränkungen
	•	Intervals.icu erlaubt keine eigenen Höhenmeterfelder → Höhenziele stehen in der Beschreibung.
	•	“Strength” muss als "WeightTraining" gemappt werden.
	•	“steps” werden in Intervals angezeigt, aber nicht im Workout-Builder editierbar (API-Limit).

⸻

✔ Fertig

Dies ist die dokumentierte & stabile Version deines Automatisierungssystems.
Wenn du möchtest, kann ich noch ergänzen:
	•	Diagramm der Pipeline
	•	Beispiel-Videos
	•	Test-Suite
	•	GitHub-Repository-Skelett

Sag einfach Bescheid!