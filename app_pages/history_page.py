from datetime import datetime
import base64
import pandas as pd
import streamlit as st
from core.history_manager import HistoryManager


class HistoryPage:
    def __init__(self, history_manager: HistoryManager):
        # Salvam obiectul HistoryManager pentru a accesa istoricul utilizatorului
        self.history = history_manager

    def render(self):
        # Titlul principal al paginii
        st.title("Istoricul tau")

        # Preluam istoricul utilizatorului curent
        user_history = self.history.get_user_history()

        # Daca nu exista istoric, afisam un mesaj si oprim executia
        if not user_history:
            st.info("Nu ai inca istoric.")
            return

        # Construim o lista de randuri pentru DataFrame
        rows = []
        for entry in reversed(user_history):  # reversed = cele mai noi intrari apar primele
            rows.append(
                {
                    "Data": entry.get("timestamp", ""),
                    "Preparat": entry.get("dish_name", "unknown"),
                    "Calorii": entry.get("total_calories", 0),
                    "Proteine": entry.get("total_protein", 0),
                    "Carbohidrati": entry.get("total_carbs", 0),
                    "Grasimi": entry.get("total_fat", 0),
                    "Image": entry.get("image_b64"),  # imaginea salvata in format Base64
                }
            )

        # Convertim lista intr-un DataFrame pentru filtrare si afisare
        df = pd.DataFrame(rows)

        # Convertim coloana Data in format datetime pentru filtrare corecta
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

        # Sectiunea de filtre
        st.subheader("Filtre")
        col1, col2 = st.columns(2)

        # Filtru dupa numele preparatului
        with col1:
            filter_name = st.text_input("Cauta dupa numele preparatului")

        # Filtru dupa intervalul de date
        with col2:
            # Extragem doar date valide pentru a calcula intervalul minim-maxim
            valid_dates = df["Data"].dropna()
            if len(valid_dates) > 0:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
            else:
                # Daca nu exista date valide, folosim data curenta
                today = datetime.now().date()
                min_date = today
                max_date = today

            # Selector de interval de date
            date_range = st.date_input(
                "Alege intervalul de date", value=(min_date, max_date)
            )

        # Aplicam filtrul dupa numele preparatului
        if filter_name:
            df = df[df["Preparat"].str.contains(filter_name, case=False, na=False)]

        # Aplicam filtrul dupa intervalul de date
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = date_range
            df = df[(df["Data"].dt.date >= start) & (df["Data"].dt.date <= end)]

        # Afisam tabelul filtrat (fara coloana Image)
        st.subheader("Tabel istoric filtrat")
        st.dataframe(df.drop(columns=["Image"]), use_container_width=True)

        # Sectiune pentru vizualizarea imaginilor asociate fiecarei intrari
        st.subheader("Vizualizare imagini")
        for _, row in df.iterrows():
            # Expander pentru fiecare preparat
            with st.expander(f"📸 Vezi imaginea pentru: {row['Preparat']}"):
                if row["Image"]:
                    # Afisam imaginea decodata din Base64
                    st.image(
                        f"data:image/png;base64,{row['Image']}",
                        caption=row["Preparat"],
                        use_container_width=True,
                    )
                else:
                    st.info("Nu exista imagine salvata pentru aceasta intrare.")