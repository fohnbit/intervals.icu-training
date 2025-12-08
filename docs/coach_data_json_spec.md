# Coach & Plan JSON API – Spezifikation

Stand: 2025-12-08

Dieses Dokument beschreibt zwei interne JSON-Formate:

1. **Coach Data JSON** – Ausgabe von `weekly_coach_data.py`
2. **Plan Upload JSON** – Eingabe/Ausgabe für den Plan-Uploader nach Intervals.icu

Ziel: Klare, stabile „API“ für eigene Tools (CLI, GUI, Analysen).

---

## 1. Coach Data JSON

### 1.1 Root-Format

Das Ergebnis ist ein **Array von Tagen**, jeweils mit Wellness- und Aktivitätsdaten:

```json
[
  {
    "date": "YYYY-MM-DD",
    "wellness": { "...": "..." },
    "activities": [ "..." ]
  }
]
```

- `date`: Kalendertag im ISO-Format.
- `wellness`: Tages-Wellnessdaten (oder `null`).
- `activities`: Liste aller Aktivitäten an diesem Tag (kann leer sein).

---

### 1.2 Wellness-Objekt

Quelle: Intervals.icu `/wellness` API.
Viele Werte stammen indirekt aus Garmin (über Intervals).

| Feld             | Typ                     | Beschreibung                                      |
|------------------|-------------------------|---------------------------------------------------|
| `ctl`            | number \| null          | Chronic Training Load (Langzeit-Belastung)       |
| `atl`            | number \| null          | Acute Training Load (Kurzzeit-Belastung)         |
| `rampRate`       | number \| null          | Veränderung von CTL pro Woche                    |
| `ctlLoad`        | number \| null          | Gesamtlast (CTL-Modell)                          |
| `atlLoad`        | number \| null          | Gesamtlast (ATL-Modell)                          |
| `weight`         | number \| null          | Körpergewicht in kg                              |
| `resting_hr`     | number \| null          | Ruhepuls                                          |
| `hrv`            | number \| null          | HRV (ms) – je nach Quelle                        |
| `hrv_sdnn`       | number \| null          | HRV SDNN                                          |
| `kcal_consumed`  | number \| null          | Getrackte zugeführte kcal                        |
| `sleep_secs`     | number \| null          | Schlafdauer in Sekunden                          |
| `sleep_hours`    | number \| null          | Schlafdauer in Stunden (abgeleitet)              |
| `sleep_score`    | number \| null          | Schlafscore                                      |
| `sleep_quality`  | number \| string \| null| Schlafqualität (z. B. Skala oder Text)           |
| `avg_sleeping_hr`| number \| null          | Durchschnittliche HF im Schlaf                   |
| `steps`          | integer \| null         | Tages-Schritte (z. B. von Garmin)               |
| `updated`        | string \| null          | Zeitstempel letzte Aktualisierung                |

Das gesamte Wellness-Objekt kann `null` sein, wenn keine Daten vorhanden sind.

---

### 1.3 Activity-Objekt

Quelle: Intervals.icu `/activities` API.

| Feld             | Typ                     | Beschreibung                                      |
|------------------|-------------------------|---------------------------------------------------|
| `date`           | string                  | Datum (YYYY-MM-DD) der Aktivität                 |
| `id`             | string \| number \| null| Intervals-Aktivitäts-ID                          |
| `name`           | string \| null          | Titel der Aktivität                              |
| `type`           | string \| null          | Typ (Ride, Run, VirtualRide, Strength, …)        |
| `duration_s`     | integer \| null         | Gesamtdauer (elapsed time) in Sekunden           |
| `moving_s`       | integer \| null         | Bewegungszeit in Sekunden                        |
| `distance_m`     | number \| null          | Distanz in Metern                                |
| `elevation_gain_m`| number \| null         | Höhenmeter                                       |
| `training_load`  | number \| null          | Trainingslast (TL/TSS)                           |
| `np_est`         | number \| null          | Normalized Power (Schätzung)                     |
| `avg_power`      | number \| null          | Durchschnittsleistung in Watt                    |
| `intensity_index`| number \| null          | Intensitätsindex (IF)                            |
| `strain_score`   | number \| null          | Intervals Strain Score                           |
| `avg_hr`         | number \| null          | Durchschnittspuls                                |
| `max_hr`         | number \| null          | Maximalpuls                                      |
| `session_rpe`    | number \| null          | Session RPE (subjektive Anstrengung)             |
| `feeling`        | number \| null          | Feeling-Skala (z. B. 1–5)                        |
| `notes`          | string \| null          | Notizen / Beschreibung                           |
| `trainer`        | boolean \| null         | True, wenn Indoor-Training                       |
| `commute`        | boolean \| null         | Pendelstrecke                                    |
| `race`           | boolean \| null         | Wettkampf                                        |
| `device_name`    | string \| null          | Gerätename (Garmin, Wahoo, …)                    |
| `source`         | string \| null          | Importquelle                                     |

Aktivitäten-Array kann leer sein, wenn an einem Tag nichts aufgezeichnet wurde.

---

## 2. Plan Upload JSON

Dieses Format wird vom Plan-Uploader genutzt, um Workouts nach Intervals.icu zu schreiben.

Es existieren zwei Varianten:

1. **Top-Level-Array** von Workouts
2. Ein Objekt mit Feld `trainings: [ … ]`

### 2.1 Top-Level-Formate

**Variante A – Array:**

```json
[
  { "date": "2025-03-01", "name": "GA1", "plan_id": "2025-W1-D1" },
  { "date": "2025-03-02", "name": "SST", "plan_id": "2025-W1-D2" }
]
```

**Variante B – Objekt mit `trainings`:**

```json
{
  "trainings": [
    { "date": "2025-03-01", "name": "GA1", "plan_id": "2025-W1-D1" }
  ]
}
```

Dein Loader (`load_plan_file`) unterstützt **beide**.

---

### 2.2 Workout-Objekt

Typisches Workout-JSON (vereinfacht):

```json
{
  "date": "2025-03-01",
  "name": "GA1 locker + 3x3' SS",
  "plan_id": "2025-W1-D1",
  "category": "WORKOUT",
  "type": "ride",
  "description": "GA1 locker, in der Mitte 3x3' Sweetspot",
  "moving_time": 5400,
  "duration_minutes": 90,
  "steps": [
    {
      "duration": "15m",
      "zone": "Z1",
      "cadence": "85rpm",
      "intensity": "warmup",
      "ramp": false
    },
    {
      "duration": "3m",
      "zone": "SS",
      "cadence": "90rpm",
      "intensity": "active",
      "ramp": false
    }
  ]
}
```

#### Wichtige Felder:

| Feld               | Typ              | Pflicht | Beschreibung                                      |
|--------------------|------------------|---------|---------------------------------------------------|
| `date`             | string           | ja      | Datum des geplanten Workouts (YYYY-MM-DD)         |
| `name`             | string           | ja      | Klarer Name                                       |
| `plan_id`          | string           | ja      | Eindeutige ID für Matching / Update in Intervals  |
| `category`         | string           | nein    | Z. B. `WORKOUT`                                   |
| `type` / `sport`   | string           | nein    | Z. B. `ride`, `run`, `strength`                   |
| `description`      | string           | nein    | Frei-Text Beschreibung                            |
| `moving_time`      | integer          | nein    | Gesamtdauer in Sekunden (Fallback, wenn keine Steps) |
| `duration_minutes` | number           | nein    | Gesamtdauer in Minuten (Fallback)                 |
| `steps`            | array of objects | nein    | Strukturierter Ablauf des Workouts                |

Hinweis: `type` oder `sport` wird auf einen gültigen Intervals-Eventtyp gemappt (Ride, Run, WeightTraining, VirtualRow, …).

---

### 2.3 Step-Objekt

Jeder Step beschreibt einen Abschnitt im Workout:

```json
{
  "duration": "10m",
  "zone": "Z2",
  "cadence": "90rpm",
  "intensity": "active",
  "ramp": false
}
```

| Feld         | Typ       | Pflicht | Beschreibung                                      |
|--------------|-----------|---------|---------------------------------------------------|
| `duration`   | string    | ja      | Dauer, z. B. `10m` oder `30s`                    |
| `zone`       | string    | nein    | Trainingszone (`Z1`, `Z2`, `SS`, `Z5`, …)        |
| `cadence`    | string    | nein    | Trittfrequenz, z. B. `90rpm` oder `90-100rpm`    |
| `intensity`  | string    | nein    | Logischer Status (`warmup`, `active`, `recovery`, `cooldown`) |
| `ramp`       | boolean   | nein    | Ob es sich um einen Ramp-Step handelt            |

---

### 2.4 Verknüpfung mit Intervals.icu Events

Beim Erzeugen/Updaten von Events werden folgende Dinge gemacht:

- Die `plan_id` wird in der Beschreibung kodiert:  
  `"[PLAN-ID:2025-W1-D1]"`
- Die Beschreibung (`description`) aus dem JSON kommt **unter** die PLAN-ID.
- Danach folgen die Steps als Textzeilen, z. B.:  
  `- 10m Z2 90rpm intensity=active`

Dadurch kann der Updater später anhand der `PLAN-ID` erkennen, welches Event zu welchem Plan gehört und Events gezielt updaten.

---

## 3. Versionierung und Änderungen

- Änderungen an den Feldern sollten hier dokumentiert werden.
- Bei breaking changes empfiehlt sich eine `version` im Root-Objekt oder im Dateinamen (z. B. `coach_data_v2.schema.json`).

---

Ende der Spezifikation.
