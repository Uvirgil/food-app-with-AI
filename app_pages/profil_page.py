import streamlit as st
from core.calorie_settings import CalorieSettings


class ProfilePage:
    def __init__(self, settings: CalorieSettings, current_user: str):
        # Salvam obiectul CalorieSettings pentru a modifica limitele calorice
        self.settings = settings

        # Salvam numele utilizatorului curent pentru afisare
        self.current_user = current_user

    def render(self):
        # Titlul principal al paginii de profil
        st.title("Profil utilizator")

        # Afisam numele utilizatorului logat
        st.write(f"Username: **{self.current_user}**")

        # Linie de separare vizuala
        st.markdown("---")

        # Sectiunea pentru setarile calorice
        st.subheader("Setari calorii")

        # Mesaj informativ despre rolul acestor setari
        st.info(
            "Ajusteaza limitele zilnice si saptamanale. "
            "Acestea sunt folosite in calendar si in raportul saptamanal."
        )

        # Input pentru limita minima zilnica de calorii
        self.settings.min_daily = st.number_input(
            "Limita minima (kcal/zi)",
            min_value=0,
            max_value=5000,
            value=self.settings.min_daily,
        )

        # Input pentru limita maxima zilnica de calorii
        self.settings.max_daily = st.number_input(
            "Limita maxima (kcal/zi)",
            min_value=0,
            max_value=5000,
            value=self.settings.max_daily,
        )

        # Input pentru limita minima saptamanala de calorii
        self.settings.min_weekly = st.number_input(
            "Limita minima (kcal/saptamana)",
            min_value=0,
            max_value=50000,
            value=self.settings.min_weekly,
        )

        # Input pentru limita maxima saptamanala de calorii
        self.settings.max_weekly = st.number_input(
            "Limita maxima (kcal/saptamana)",
            min_value=0,
            max_value=50000,
            value=self.settings.max_weekly,
        )

        # Mesaj de confirmare ca setarile au fost actualizate
        st.success("Setarile au fost salvate.")