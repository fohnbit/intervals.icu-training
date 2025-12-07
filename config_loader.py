import json
from pathlib import Path

CONFIG_PATH = Path("config.json")


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Konfigurationsdatei nicht gefunden: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
