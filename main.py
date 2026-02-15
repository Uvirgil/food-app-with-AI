import streamlit as st

from core.auth_manager import AuthManager
from core.calorie_settings import CalorieSettings
from core.history_manager import HistoryManager
from core.vision import VisionAnalyzer

from app_pages.home_page import HomePage
from app_pages.history_page import HistoryPage
from app_pages.stats_page import StatsPage
from app_pages.profil_page import ProfilePage


def get_api_key():
    # Incearca sa citeasca cheia API din secrets.toml (varianta recomandata)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Daca nu exista in secrets, o importam din fisierul local secret_key.py
        from secret_key import OPENAI_API_KEY
        return OPENAI_API_KEY


def main():
        # Sectiunea din sidebar pentru autentificare
        st.sidebar.title("Autentificare")
        auth = AuthManager()

        # Alegem intre Login si Creare cont
        mode = st.sidebar.radio("Alege actiunea:", ["Login", "Creeaza cont"])

        # Input pentru username si parola
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Parola", type="password")

        # Logica pentru creare cont
        if mode == "Creeaza cont":
            if st.sidebar.button("Creeaza cont"):
                if not username or not password:
                    st.sidebar.error("Completeaza username si parola.")
                else:
                    if auth.register(username, password):
                        st.sidebar.success("Cont creat cu succes! Acum te poti loga.")
                    else:
                        st.sidebar.error("Username deja existent.")

        # Logica pentru login
        if mode == "Login":
            if st.sidebar.button("Login"):
                user = auth.login(username, password)
                if user:
                    # Salvam utilizatorul in session_state pentru persistenta
                    st.session_state["user"] = user
                    st.sidebar.success(f"Autentificat ca: {user}")
                else:
                    st.sidebar.error("Date incorecte.")

        # Daca utilizatorul nu este logat, oprim executia paginii
        if "user" not in st.session_state:
            st.warning("Te rog autentifica-te in stanga.")
            return

        # Preluam username-ul utilizatorului curent
        current_user = st.session_state["user"]

        # Meniu de navigare in sidebar
        st.sidebar.markdown("---")
        page = st.sidebar.radio("Navigare", ["Home", "Istoric", "Statistici", "Profil"])

        # Initializam obiectele necesare pentru pagini
        settings = CalorieSettings(st.session_state)
        vision = VisionAnalyzer(api_key=get_api_key())
        history = HistoryManager(current_user)

        # Navigare intre pagini
        if page == "Home":
            HomePage(vision, history).render()
        elif page == "Istoric":
            HistoryPage(history).render()
        elif page == "Statistici":
            StatsPage(history, settings).render()
        elif page == "Profil":
            ProfilePage(settings, current_user).render()


# if __name__ == "__main__":
#     main()