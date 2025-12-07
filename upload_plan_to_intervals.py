import requests
import json
import datetime
from pathlib import Path
from config_loader import load_config

config = load_config()

API_KEY = config["api_key"]
ATHLETE_ID = config["athlete_id"]
BASE_URL = config["base_url"]
PLAN_FILE = config["paths"].get("plan_file")
PLAN_DIR = config["paths"].get("plan_dir")
DEFAULT_START_TIME = config.get("default_start_time", "17:00:00")

# Marker-Format in der Beschreibung für Matching
PLAN_MARKER_PREFIX = "[PLAN-ID:"
PLAN_MARKER_SUFFIX = "]"


def auth():
    # entspricht "API_KEY:<api_key>" Basic Auth
    return ("API_KEY", API_KEY)


def load_plan_file(path: str):
    """
    Lädt einen einzelnen Plan aus einer JSON-Datei.
    Erwartet:
    - eine Liste von Workouts (unser aktuelles Format), ODER
    - ein Dict mit 'trainings' (kompatibel zum GitHub-Beispiel).

    Die Workouts selbst enthalten bereits:
    - steps mit duration, zone, cadence, description
    - optional intensity, ramp, ...
    Diese Felder werden später 1:1 an Intervals.icu durchgereicht.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Plan-Datei nicht gefunden: {path}")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "trainings" in data:
        return data["trainings"]

    raise ValueError(f"Unbekanntes JSON-Format in {path}")


def load_all_workouts() -> list[dict]:
    """
    Lädt Workouts aus:
    - allen JSON-Dateien in PLAN_DIR (falls gesetzt)
    - ansonsten aus PLAN_FILE

    Filtert anschließend alle Workouts < HEUTE heraus.
    """
    workouts: list[dict] = []

    if PLAN_DIR:
        d = Path(PLAN_DIR)
        if not d.exists():
            raise FileNotFoundError(
                f"Trainingsverzeichnis nicht gefunden: {PLAN_DIR}"
            )

        json_files = sorted(d.glob("*.json"))
        if not json_files:
            print(f"Keine .json-Dateien in {PLAN_DIR} gefunden.")
        else:
            print(
                f"Lade Workouts aus {len(json_files)} Dateien in {PLAN_DIR} ...")
        for jf in json_files:
            try:
                file_data = load_plan_file(str(jf))
                if not isinstance(file_data, list):
                    print(f"Überspringe {jf}: kein Array von Workouts")
                    continue
                workouts.extend(file_data)
            except Exception as e:
                print(f"Fehler beim Laden von {jf}: {e}")
    else:
        # Fallback: einzelnes Plan-File wie bisher
        if not PLAN_FILE:
            raise RuntimeError(
                "Weder plan_dir noch plan_file in config.paths gesetzt."
            )
        print(f"Lade Workouts aus Plan-Datei: {PLAN_FILE}")
        workouts = load_plan_file(PLAN_FILE)

    # Filter: nur Workouts ab heute
    today = datetime.date.today()
    filtered: list[dict] = []
    for w in workouts:
        date_str = w.get("date")
        if not date_str:
            continue
        try:
            d = datetime.date.fromisoformat(date_str)
        except Exception:
            print(f"Ungültiges Datum im Workout (wird ignoriert): {date_str}")
            continue
        if d >= today:
            filtered.append(w)

    print(
        f"Gefundene Workouts gesamt: {len(workouts)}, davon ab heute: {len(filtered)}"
    )
    return filtered


def get_date_range_from_plan(plan: list[dict]):
    dates = [datetime.date.fromisoformat(w["date"]) for w in plan]
    return min(dates), max(dates)


def map_sport_to_event_type(sport: str) -> str:
    """
    Mappt unser internes 'sport'/'type'-Feld auf einen gültigen Intervals.icu-Eventtyp.
    """
    s = (sport or "").lower()

    if s == "ride":
        return "Ride"
    if s in ("strength", "gym", "kraft", "weighttraining"):
        return "WeightTraining"
    if s in ("virtualrow", "row", "rowing"):
        return "VirtualRow"
    if s in ("run", "lauf", "laufen"):
        return "Run"

    # Fallback – sicherer generischer Typ
    return "Workout"


def fetch_existing_events(start_date: datetime.date, end_date: datetime.date):
    """
    Holt alle Events im Datumsbereich.
    """
    url = f"{BASE_URL}/athlete/{ATHLETE_ID}/events"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat(),
    }
    resp = requests.get(url, auth=auth(), params=params, timeout=30)
    if not resp.ok:
        print("Fehler beim Laden vorhandener Events")
        print("Status:", resp.status_code)
        print("Antwort:", resp.text)
        resp.raise_for_status()
    return resp.json()


def convert_duration(duration: str) -> int:
    """
    Konvertiert Dauer-Strings wie '10m', '30s' in Sekunden.
    (Nur für moving_time, nicht für die Description.)
    """
    if not duration:
        return 0
    duration = duration.strip()

    if duration.endswith("m"):
        val = float(duration.replace("m", "").strip())
        return int(val * 60)
    elif duration.endswith("s"):
        val = float(duration.replace("s", "").strip())
        return int(val)
    else:
        return int(float(duration))


def build_description_with_steps(plan_id: str, steps: list[dict]) -> str:
    """
    Baut die description im gewünschten Stil:

    [PLAN-ID:...]
    - 15m ramp Z1 Free intensity=warmup
    - 8m SS 90rpm intensity=active
    - 5m Z1 Free intensity=recovery
    ...

    Regeln:
    - kein "in" mehr
    - "ramp" kommt direkt nach der Dauer, falls im Step gesetzt
    - intensity wird als "intensity=<wert>" angehängt, falls vorhanden
    """
    lines: list[str] = []

    # PLAN-ID als erste Zeile (für's Matching beim Upsert)
    if plan_id:
        lines.append(f"{PLAN_MARKER_PREFIX}{plan_id}{PLAN_MARKER_SUFFIX}")

    for step in steps:
        dur = (step.get("duration") or "").strip()
        zone = (step.get("zone") or "").strip()
        cadence = (step.get("cadence") or "").strip()
        intensity = (step.get("intensity") or "").strip()
        ramp_flag = bool(step.get("ramp"))

        if not dur:
            continue

        # Basis: "- 15m"
        line_parts = [f"- {dur}"]

        # ramp direkt nach der Zeit
        if ramp_flag:
            line_parts.append("ramp")

        # Zone (SS, Z1, Z2, Z3, Z5, ...)
        if zone:
            line_parts.append(zone)

        # Kadenz (inkl. Bereiche wie 90-100rpm oder "Free")
        if cadence:
            line_parts.append(cadence)

        # intensity hinten anhängen
        if intensity:
            line_parts.append(f"intensity={intensity}")

        line = " ".join(line_parts)
        lines.append(line)

    return "\n".join(lines).strip()

def extract_plan_id_from_description(description: str | None) -> str | None:
    """
    Liest PLAN-ID aus der description, wenn vorhanden.
    Sucht nach Muster: [PLAN-ID:...]
    """
    if not description:
        return None
    text = description

    start = text.find(PLAN_MARKER_PREFIX)
    if start == -1:
        return None
    end = text.find(PLAN_MARKER_SUFFIX, start)
    if end == -1:
        return None

    inner = text[start + len(PLAN_MARKER_PREFIX):end].strip()
    return inner or None


def build_event_payload(workout: dict) -> dict:
    """
    Baut den Payload für ein Intervals.icu-Event aus einem Plan-Eintrag.
    WICHTIG:
    - Description im Format "- 10m in Z2 85rpm" aus steps
    - moving_time aus steps bzw. aus duration/moving_time im Plan
    - steps werden 1:1 übernommen, inkl. intensity, ramp, etc.
    """
    date = workout["date"]
    start_date_local = f"{date}T{DEFAULT_START_TIME}"

    steps = workout.get("steps", []) or []

    # moving_time: Summe der Step-Dauern, sonst Fallback
    if steps:
        total_secs = 0
        for s in steps:
            dstr = s.get("duration")
            if not dstr:
                continue
            total_secs += convert_duration(dstr)
        moving_time = total_secs
    else:
        if "moving_time" in workout and workout["moving_time"] is not None:
            moving_time = int(workout["moving_time"])
        elif (
            "duration_minutes" in workout
            and workout["duration_minutes"] is not None
        ):
            moving_time = int(round(workout["duration_minutes"] * 60))
        else:
            moving_time = None

    category = workout.get("category", "WORKOUT")
    plan_id = workout["plan_id"]

    # sport entweder aus 'sport' (alte Struktur) oder aus 'type' (neue Struktur)
    raw_sport = workout.get("sport") or workout.get("type") or ""

    description = build_description_with_steps(plan_id, steps)

    payload = {
        "start_date_local": start_date_local,
        "category": category,
        "name": workout["name"],
        "description": description,
        "type": map_sport_to_event_type(raw_sport),
        "moving_time": moving_time,
        # Hier werden intensity / ramp etc. automatisch mitgeschickt
        "steps": steps,
    }

    return payload


def index_events_by_plan_id_from_description(
    events: list[dict],
) -> dict[str, dict]:
    """
    Erstellt ein Dict: plan_id -> Event
    indem die PLAN-ID aus der description extrahiert wird.
    """
    by_plan_id: dict[str, dict] = {}

    for e in events:
        desc = e.get("description") or ""
        plan_id = extract_plan_id_from_description(desc)
        if plan_id:
            by_plan_id[plan_id] = e

    return by_plan_id


def upsert_plan(plan: list[dict]):
    if not plan:
        print("Kein Workout im Plan (ab heute) – nichts zu tun.")
        return

    start_date, end_date = get_date_range_from_plan(plan)
    print(f"Datumsbereich im Plan (ab heute): {start_date} bis {end_date}")

    print("Lade existierende Events aus Intervals.icu ...")
    existing_events = fetch_existing_events(start_date, end_date)
    events_by_plan_id = index_events_by_plan_id_from_description(
        existing_events)
    print(
        f"Gefundene Events mit PLAN-ID in description: {len(events_by_plan_id)}"
    )

    new_events_payloads = []
    updated = 0

    for workout in plan:
        plan_id = workout["plan_id"]
        payload = build_event_payload(workout)

        existing = events_by_plan_id.get(plan_id)

        if existing:
            event_id = existing["id"]
            url = f"{BASE_URL}/athlete/{ATHLETE_ID}/events/{event_id}"
            print(f"Update Event {event_id} (plan_id={plan_id}) ...")
            resp = requests.put(url, auth=auth(), json=payload, timeout=30)
            if not resp.ok:
                print(
                    f"\n❌ Fehler beim Update von Event {event_id} (plan_id={plan_id})"
                )
                print("Payload (PUT):")
                print(json.dumps(payload, indent=2, ensure_ascii=False))
                print("Status:", resp.status_code)
                print("Antwort:", resp.text)
                raise SystemExit(1)
            updated += 1
        else:
            print(f"Plane neues Event (plan_id={plan_id}) zur Erstellung ...")
            new_events_payloads.append(payload)

    created = 0
    if new_events_payloads:
        url = f"{BASE_URL}/athlete/{ATHLETE_ID}/events/bulk"
        print(f"Sende {len(new_events_payloads)} neue Events an {url} ...")
        resp = requests.post(
            url, auth=auth(), json=new_events_payloads, timeout=30
        )
        if not resp.ok:
            print("\n❌ Fehler beim Erstellen neuer Events (bulk)")
            print("Payload (POST bulk):")
            print(json.dumps(new_events_payloads, indent=2, ensure_ascii=False))
            print("Status:", resp.status_code)
            print("Antwort:", resp.text)
            raise SystemExit(1)

        created = len(new_events_payloads)

    print(f"\n✅ Fertig. Neu erstellt: {created}, aktualisiert: {updated}")


def main():
    plan = load_all_workouts()
    print(f"{len(plan)} Einheiten im Plan (ab heute).")
    upsert_plan(plan)


if __name__ == "__main__":
    main()
