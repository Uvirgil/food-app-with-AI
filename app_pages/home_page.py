import io
import ast
import json
import base64
import pandas as pd
import streamlit as st
from PIL import Image
from core.history_manager import HistoryManager
from core.vision import VisionAnalyzer


class HomePage:
    def __init__(self, vision: VisionAnalyzer, history_manager: HistoryManager):
        # Salvam obiectele necesare pentru analiza imaginilor si gestionarea istoricului
        self.vision = vision
        self.history = history_manager

    def render(self):
        # Titlul principal al paginii
        st.title("🍽️ Aplicatia de recunoastere a alimentelor")

        # Text explicativ pentru utilizator
        st.write(
            "Incarca o poza cu mancare si iti dau o estimare detaliata de calorii si macronutrienti."
        )

        # Uploader pentru imagine (accepta doar formate foto)
        uploaded = st.file_uploader("Incarca o imagine", type=["jpg", "jpeg", "png"])

        # Daca nu a fost incarcata nicio imagine, oprim executia
        if not uploaded:
            return

        # Deschidem imaginea folosind PIL
        img = Image.open(uploaded)

        # Afisam imaginea incarcata in aplicatie
        st.image(img, caption="Imagine incarcata", use_container_width=True)

        # Trimitem imaginea catre modelul AI pentru analiza
        result = self.vision.analyze(img)

        # Incercam sa convertim raspunsul AI in format JSON
        try:
            data = json.loads(result)
        except Exception:
            # Daca nu este JSON valid, incercam sa il interpretam ca dictionar Python
            try:
                data = ast.literal_eval(result)
            except Exception:
                # Daca nici asa nu merge, afisam eroarea si oprim executia
                st.error("AI a returnat un format invalid.")
                st.write(result)
                return

        # Extragem informatiile principale din raspunsul AI
        ingredients = data.get("ingredients", [])
        dish_name = data.get("dish_name", "unknown dish")
        total_cal = data.get("total_calories", 0)
        total_protein = data.get("total_protein", 0)
        total_carbs = data.get("total_carbs", 0)
        total_fat = data.get("total_fat", 0)

        # Convertim imaginea in Base64 pentru a o salva in istoric
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Salvam intrarea in istoricul utilizatorului
        self.history.add(
            dish_name,
            total_cal,
            total_protein,
            total_carbs,
            total_fat,
            img_b64,
            ingredients,
        )

        # Afisam numele preparatului detectat
        st.subheader(f"Preparat detectat: {dish_name}")

        # Afisam totalul de calorii
        st.success(f"Total calorii estimate: {total_cal} kcal")

        # Afisam macronutrientii principali
        st.subheader("Macronutrienti totali:")
        st.write(f"Proteine: {total_protein} g")
        st.write(f"Carbohidrati: {total_carbs} g")
        st.write(f"Grasimi: {total_fat} g")

        # Afisam tabelul cu ingredientele detectate
        st.subheader("Ingrediente detectate (tabel):")
        if ingredients:
            # Construim DataFrame cu ingredientele si valorile lor nutritionale
            df_ing = pd.DataFrame(
                [
                    {
                        "Ingredient": ing.get("name", "unknown"),
                        "Calorii (kcal)": ing.get("calories", 0),
                        "Proteine (g)": ing.get("protein", 0),
                        "Carbohidrati (g)": ing.get("carbs", 0),
                        "Grasimi (g)": ing.get("fat", 0),
                    }
                    for ing in ingredients
                ]
            )
            # Afisam tabelul
            st.table(df_ing)
        else:
            # Daca AI nu a detectat ingrediente clare
            st.info("Nu au fost detectate ingrediente in mod clar.")