from typing import List, Dict, Any
from history import load_history, add_entry


class HistoryManager:
    def __init__(self, user: str):
        # Salvam username-ul utilizatorului curent pentru a-i gestiona istoricul
        self.user = user

    def get_user_history(self) -> List[Dict[str, Any]]:
        # Incarcam istoricul complet din fisier/baza de date
        history = load_history()

        # Returnam doar istoricul utilizatorului curent
        # Daca nu exista intrari, intoarcem lista goala
        return history.get(self.user, [])

    def add(
        self,
        dish_name: str,
        total_cal: float,
        total_protein: float,
        total_carbs: float,
        total_fat: float,
        img_b64: str,
        ingredients: list,
    ) -> None:
        # Adaugam o noua intrare in istoricul utilizatorului
        # Functia add_entry se ocupa de salvarea efectiva
        add_entry(
            self.user,
            dish_name,
            total_cal,
            total_protein,
            total_carbs,
            total_fat,
            img_b64,
            ingredients,
        )