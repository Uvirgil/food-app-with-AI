import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def add_entry(
    user: str,
    dish_name: str,
    total_cal: float,
    total_protein: float,
    total_carbs: float,
    total_fat: float,
    img_b64: str,
    ingredients: list,
):
    history = load_history()

    if user not in history:
        history[user] = []

    entry = {
        "date": datetime.now().isoformat(),

        "dish_name": dish_name,
        "total_calories": total_cal,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat,
        "image": img_b64,
        "ingredients": ingredients,
    }

    history[user].append(entry)

    save_history(history)