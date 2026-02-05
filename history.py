import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def add_entry(username, dish_name, total_calories, total_protein, total_carbs, total_fat, image_b64, ingredients):
    history = load_history()

    if username not in history:
        history[username] = []

    now = datetime.now()
    entry = {
        "dish_name": dish_name,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat,
        "ingredients": ingredients,
        "timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "date": now.strftime("%Y-%m-%d"),
        "image_b64": image_b64
    }

    history[username].append(entry)
    save_history(history)