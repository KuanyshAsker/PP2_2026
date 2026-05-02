import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

DEFAULT_SETTINGS = {
    # Default values are used if settings.json is empty or broken.
    "screen_width": 400,
    "screen_height": 600,
    "fps": 60,
    "music_volume": 0.5,
    "player_speed": 5,
    "enemy_speed": 5,
    "coin_speed": 5,
    "track_object_speed": 5,
    "base_traffic_delay": 1800,
    "base_obstacle_delay": 2300,
    "base_power_up_delay": 6500,
    "power_up_timeout": 7000,
    "race_distance": 5000,
    "sound_enabled": True,
    "car_color": "Blue",
    "difficulty": "Normal",
}


def read_json(path, default_value):
    # Small safe reader so the game does not crash if json is empty.
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return default_value

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_value


def write_json(path, data):
    # Save with indent so the json file is readable for checking.
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_settings():
    # Load saved settings, but keep any missing keys from DEFAULT_SETTINGS.
    settings = DEFAULT_SETTINGS.copy()
    saved_settings = read_json(SETTINGS_FILE, {})

    if isinstance(saved_settings, dict):
        settings.update(saved_settings)

    write_json(SETTINGS_FILE, settings)
    return settings


def save_settings(settings):
    # Used by the settings screen when player changes sound/color/difficulty.
    updated_settings = DEFAULT_SETTINGS.copy()
    updated_settings.update(settings)
    write_json(SETTINGS_FILE, updated_settings)
    return updated_settings


def load_leaderboard():
    # Leaderboard is stored as a list of dictionaries.
    leaderboard = read_json(LEADERBOARD_FILE, [])

    if isinstance(leaderboard, list):
        return leaderboard

    return []


def save_leaderboard(leaderboard):
    # Sort best scores first and keep only top 10.
    leaderboard = sorted(
        leaderboard,
        key=lambda item: (
            item.get("score", 0),
            item.get("distance", 0),
        ),
        reverse=True,
    )
    write_json(LEADERBOARD_FILE, leaderboard[:10])


def add_leaderboard_entry(name, score, distance, coins, checkpoints):
    # Add one finished run to the leaderboard file.
    leaderboard = load_leaderboard()
    leaderboard.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name": name,
            "score": score,
            "distance": distance,
            "coins": coins,
            "checkpoints": checkpoints,
        }
    )
    save_leaderboard(leaderboard)
