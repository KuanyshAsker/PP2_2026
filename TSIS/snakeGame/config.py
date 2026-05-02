import json
import os
import copy
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"

# Default values in case settings.json is missing or half-empty.
# Basically the game still has a plan B, lol.
DEFAULT_SETTINGS = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "dbname": "snake_game",
        "user": "postgres",
        "password": "postgres"
    },
    "preferences": {
        "snake_color": [0, 210, 90],
        "grid_overlay": True,
        "sound": True
    }
}


def load_settings():
    """Load project settings, falling back to defaults for missing keys."""
    settings = copy.deepcopy(DEFAULT_SETTINGS)

    # Merge saved values with defaults so old json files don't break the game.
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            user_settings = json.load(file)

        settings["database"] = {
            **DEFAULT_SETTINGS["database"],
            **user_settings.get("database", {})
        }
        settings["preferences"] = {
            **DEFAULT_SETTINGS["preferences"],
            **user_settings.get("preferences", {})
        }

    return settings


def save_settings(settings):
    """Save all settings to the local JSON file."""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def get_db_config():
    """Return psycopg2 connection settings with optional environment overrides."""
    database = load_settings()["database"]

    return {
        "host": os.getenv("SNAKE_DB_HOST", database["host"]),
        "port": int(os.getenv("SNAKE_DB_PORT", database["port"])),
        "dbname": os.getenv("SNAKE_DB_NAME", database["dbname"]),
        "user": os.getenv("SNAKE_DB_USER", database["user"]),
        "password": os.getenv("SNAKE_DB_PASSWORD", database["password"])
    }


def load_preferences():
    """Return saved gameplay preferences."""
    preferences = load_settings()["preferences"]
    color = preferences.get("snake_color", DEFAULT_SETTINGS["preferences"]["snake_color"])

    if len(color) != 3:
        color = DEFAULT_SETTINGS["preferences"]["snake_color"]

    preferences["snake_color"] = [max(0, min(255, int(value))) for value in color]
    preferences["grid_overlay"] = bool(preferences.get("grid_overlay", True))
    preferences["sound"] = bool(preferences.get("sound", True))

    return preferences


def save_preferences(preferences):
    """Save gameplay preferences while keeping database settings intact."""
    # Only preferences change here, db login stays untouched.
    settings = load_settings()
    settings["preferences"] = {
        **DEFAULT_SETTINGS["preferences"],
        **preferences
    }
    save_settings(settings)
