import requests
import datetime
import json
import argparse
from config_loader import load_config

config = load_config()

API_KEY = config["api_key"]
ATHLETE_ID = config["athlete_id"]
BASE_URL = config["base_url"]
WEEKLY_FILE = config["paths"].get("weekly_output", "weekly_coach_data.json")


def auth():
    return ("API_KEY", API_KEY)


def get_date_range(days=7):
    """
    Standardverhalten: letzte `days` Tage bis heute.
    (Wie bisher genutzt.)
    """
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days)
    return start, today


def fetch_activities(start_date, end_date):
    url = f"{BASE_URL}/athlete/{ATHLETE_ID}/activities"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat(),
    }
    r = requests.get(url, auth=auth(), params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    activities = []
    for a in data:
        raw_date = a.get("start_date_local") or a.get("start_date")
        parsed_date = None
        if raw_date:
            dstr = raw_date.split("T")[0]
            try:
                parsed_date = datetime.date.fromisoformat(dstr)
            except ValueError:
                parsed_date = None

        if parsed_date is None or not (start_date <= parsed_date <= end_date):
            continue

        activities.append({
            "date": parsed_date.isoformat(),
            "id": a.get("id"),
            "name": a.get("name"),
            "type": a.get("type"),
            "duration_s": a.get("elapsed_time"),
            "moving_s": a.get("moving_time"),
            "distance_m": a.get("distance"),
            "elevation_gain_m": a.get("total_elevation_gain"),
            "training_load": a.get("icu_training_load"),
            "np_est": a.get("icu_weighted_avg_watts"),
            "avg_power": a.get("icu_average_watts"),
            "intensity_index": a.get("icu_intensity"),
            "strain_score": a.get("strain_score"),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "session_rpe": (
                a.get("session_rpe")
                or a.get("icu_rpe")
                or a.get("perceived_exertion")
            ),
            "feeling": a.get("feel"),
            "notes": a.get("description"),
            "trainer": a.get("trainer"),
            "commute": a.get("commute"),
            "race": a.get("race"),
            "device_name": a.get("device_name"),
            "source": a.get("source"),
        })

    return activities


def fetch_wellness(start_date, end_date):
    url = f"{BASE_URL}/athlete/{ATHLETE_ID}/wellness"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat(),
    }
    r = requests.get(url, auth=auth(), params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    wellness_by_date = {}
    for w in data:
        dstr = w.get("id")
        if not dstr:
            continue
        try:
            d = datetime.date.fromisoformat(dstr)
        except ValueError:
            continue
        if not (start_date <= d <= end_date):
            continue

        wellness_by_date[dstr] = {
            "ctl": w.get("ctl"),
            "atl": w.get("atl"),
            "rampRate": w.get("rampRate"),
            "ctlLoad": w.get("ctlLoad"),
            "atlLoad": w.get("atlLoad"),
            "weight": w.get("weight"),
            "resting_hr": w.get("restingHR"),
            "hrv": w.get("hrv"),
            "hrv_sdnn": w.get("hrvSDNN"),
            "kcal_consumed": w.get("kcalConsumed"),
            "sleep_secs": w.get("sleepSecs"),
            "sleep_hours": (
                w.get("sleepSecs") / 3600.0 if w.get("sleepSecs") else None
            ),
            "sleep_score": w.get("sleepScore"),
            "sleep_quality": w.get("sleepQuality"),
            "avg_sleeping_hr": w.get("avgSleepingHR"),
            "steps": w.get("steps"), 
            "updated": w.get("updated"),
        }

    return wellness_by_date


def combine_coach_data(activities, wellness_by_date, start_date, end_date):
    # Aktivitäten pro Datum gruppieren
    act_by_date = {}
    for a in activities:
        act_by_date.setdefault(a["date"], []).append(a)

    combined = []
    current = start_date
    while current <= end_date:
        dstr = current.isoformat()
        combined.append({
            "date": dstr,
            "wellness": wellness_by_date.get(dstr),
            "activities": act_by_date.get(dstr, []),
        })
        current += datetime.timedelta(days=1)

    return combined


def parse_cli_date(date_str: str) -> datetime.date:
    """
    Erwartet TT-MM-YYYY, z.B. 01-03-2025.
    """
    try:
        return datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError(
            f"Ungültiges Datum '{date_str}'. Erwartetes Format: TT-MM-YYYY, z.B. 01-03-2025."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Hole Aktivitäten + Wellness aus Intervals.icu und speichere sie als JSON."
    )
    parser.add_argument(
        "--start", "-s",
        help="Startdatum im Format TT-MM-YYYY (z.B. 01-03-2025)."
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        help="Anzahl der Tage (Standard: 7)."
    )
    args = parser.parse_args()

    # Standardwert für Tage
    days = args.days if (args.days and args.days > 0) else 7

    if args.start:
        # explizites Startdatum + (optional) Tage
        try:
            start = parse_cli_date(args.start)
        except ValueError as e:
            print(e)
            return

        # end = start + (days - 1) → genau 'days' Tage
        end = start + datetime.timedelta(days=days - 1)
    else:
        # kein Startdatum → wie bisher (letzte N Tage, default 7)
        start, end = get_date_range(days)

    print(f"Zeitraum: {start} bis {end}")

    print("Hole Aktivitäten...")
    activities = fetch_activities(start, end)
    print(f"Aktivitäten: {len(activities)}")

    print("Hole Wellness-Daten...")
    wellness_by_date = fetch_wellness(start, end)
    print(f"Wellness-Tage: {len(wellness_by_date)}")

    combined = combine_coach_data(activities, wellness_by_date, start, end)

    with open(WEEKLY_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"Gespeichert in {WEEKLY_FILE}")


if __name__ == "__main__":
    main()
