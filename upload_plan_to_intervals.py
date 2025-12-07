import requests
import json
import datetime
from pathlib import Path
from config_loader import load_config

config = load_config()

API_KEY = config["api_key"]
ATHLETE_ID = config["athlete_id"]
BASE_URL = config["base_url"]
PLAN_FILE = config["paths"]["plan_file"]
DEFAULT_START_TIME = config.get("default_start_time", "17:00:00")

# Marker-Format in der Beschreibung für Matching
PLAN_MARKER_PREFIX = "[PLAN-ID:"
PLAN_MARKER_SUFFIX = "]"


def auth():
    # entspricht "API_KEY:<api_key>" Basic Auth
    return ("API_KEY", API_KEY)


def load_plan(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Plan-Datei nicht gefunden: {path}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_date_range_from_plan(plan):
    dates = [datetime.date.fromisoformat(w["date"]) for w in plan]
    return min(dates), max(dates)


def map_sport_to_event_type(sport: str) -> str:
    """
    Mappt unser internes 'sport'-Feld auf einen gültigen Intervals.icu-Eventtyp.
    """
    s = (sport or "").lower()

    if s == "ride":
        return "Ride"
    if s in ("strength", "gym", "kraft"):
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
    - 10m in Z2 85rpm
    - 3m in Z5 95rpm
    - 3m in Z4 90-100rpm
    - 10m in Z1 Free
    """
    lines: list[str] = []

    # PLAN-ID als erste Zeile (für's Matching beim Upsert)
    if plan_id:
        lines.append(f"{PLAN_MARKER_PREFIX}{plan_id}{PLAN_MARKER_SUFFIX}")

    for step in steps:
        dur = (step.get("duration") or "").strip()
        zone = (step.get("zone") or "").strip()
        cadence = (step.get("cadence") or "").strip()

        if not dur or not zone:
            continue

        # Basis: "- 3m in Z5"
        line = f"- {dur} in {zone}"

        # Kadenz einfach anhängen – ohne Klammern, auch Bereiche wie "90-100rpm"
        if cadence:
            line += f" {cadence}"

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
    - Description im Format "- 10m in Z2 (85rpm)" aus steps
    - moving_time aus steps (Sekunden)
    """
    date = workout["date"]
    start_date_local = f"{date}T{DEFAULT_START_TIME}"

    steps = workout.get("steps", []) or []

    # moving_time wie im GitHub-Script: Summe der Step-Dauern
    if steps:
        total_secs = 0
        for s in steps:
            dstr = s.get("duration")
            if not dstr:
                continue
            total_secs += convert_duration(dstr)
        moving_time = total_secs
    else:
        # Fallback: duration_minutes, falls gesetzt
        if "duration_minutes" in workout and workout["duration_minutes"] is not None:
            moving_time = int(round(workout["duration_minutes"] * 60))
        else:
            moving_time = None

    category = workout.get("category", "WORKOUT")
    sport_type = workout["sport"]  # z.B. "Ride", "Run", "VirtualRow" etc.
    plan_id = workout["plan_id"]

    description = build_description_with_steps(plan_id, steps)

    payload = {
        "start_date_local": start_date_local,
        "category": category,
        "name": workout["name"],
        "description": description,
        "type": map_sport_to_event_type(workout["sport"]),
        "moving_time": moving_time,
        "steps": steps  # optional, im GitHub-Beispiel auch enthalten
    }

    return payload


def index_events_by_plan_id_from_description(events: list[dict]) -> dict[str, dict]:
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
    start_date, end_date = get_date_range_from_plan(plan)
    print(f"Datumsbereich im Plan: {start_date} bis {end_date}")

    print("Lade existierende Events aus Intervals.icu ...")
    existing_events = fetch_existing_events(start_date, end_date)
    events_by_plan_id = index_events_by_plan_id_from_description(
        existing_events)
    print(
        f"Gefundene Events mit PLAN-ID in description: {len(events_by_plan_id)}")

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
                    f"\n❌ Fehler beim Update von Event {event_id} (plan_id={plan_id})")
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
            url, auth=auth(), json=new_events_payloads, timeout=30)
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
    plan = load_plan(PLAN_FILE)
    print(f"{len(plan)} Einheiten im Plan.")
    upsert_plan(plan)


if __name__ == "__main__":
    main()
