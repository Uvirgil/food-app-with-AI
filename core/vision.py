import io
import base64
from openai import OpenAI
from PIL import Image
import json
from ultralytics import YOLO
import requests


# class VisionAnalyzer:
#     def __init__(self, api_key: str):
#         # Initializam clientul OpenAI folosind cheia API primita
#         self.client = OpenAI(api_key=api_key)

#     def analyze(self, image: Image.Image) -> str:
#         # Convertim imaginea intr-un buffer in memorie
#         buf = io.BytesIO()
#         image.save(buf, format="PNG")

#         # Extragem bytes din imagine
#         img_bytes = buf.getvalue()

#         # Convertim imaginea in Base64 pentru a o trimite catre API
#         img_b64 = base64.b64encode(img_bytes).decode("utf-8")

#         # Construim URL-ul inline pentru imagine (data URL)
#         img_url = f"data:image/png;base64,{img_b64}"

#         # Trimitem cererea catre modelul vizual GPT
#         response = self.client.responses.create(
#             model="gpt-4o-mini",
#             input=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "input_text",
#                             "text": self._prompt(),  # promptul care cere JSON strict
#                         },
#                         {
#                             "type": "input_image",
#                             "image_url": img_url,  # imaginea codata Base64
#                         },
#                     ],
#                 }
#             ],
#         )

# import io
# import base64
# import requests
# from PIL import Image

# class VisionAnalyzer:
#     def __init__(self):
#         self.url = "http://localhost:11434/api/chat"

#     def _prompt(self):
#         return (
#             "Analizează această imagine cu mâncare și întoarce STRICT un JSON cu:\n"
#             "{ 'food': 'nume aliment', 'calories': număr estimat, 'confidence': procent' }"
#         )

#     def analyze(self, image: Image.Image) -> str:
#         try:
#             # 🔥 1. Micșorăm imaginea la max 512 px (păstrează proporțiile)
#             image.thumbnail((512, 512))
            
#             buf = io.BytesIO()
#             image.save(buf, format="PNG")
#             img_bytes = buf.getvalue()

#             img_b64 = base64.b64encode(img_bytes).decode("utf-8")

#             payload = {
#                 "model": "qwen3-vl:2b",    # sau modelul qwen3-vl:8b pentru o detectie mai avansata
#                 "stream": False,
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": self._prompt(),
#                         "images": [img_b64]
#                     }
#                 ]
#             }

#             response = requests.post(self.url, json=payload, timeout=400)

#             # folosim json.loads pentru siguranță
#             data = json.loads(response.text)

#             if "error" in data:
#                 return f"Eroare Ollama: {data['error']}"

#             if "message" in data and "content" in data["message"]:
#                 return data["message"]["content"]

#             return f"Răspuns necunoscut de la Ollama: {data}"

#         except Exception as e:
#             return f"Eroare la conectarea cu Ollama: {e}"

class VisionAnalyzer:
    def __init__(self):
        # YOLO pentru detectarea farfuriei
        self.detector = YOLO("yolov8s.pt")

        # Modelul Ollama (vizual + rapid pe CPU)
        self.ollama_model = "qwen3-vl:8b"
        self.ollama_url = "http://localhost:11434/api/chat"

    def _prompt(self):
        """Prompt optimizat pentru viteză și acuratețe."""
        return (
            "Analizează această imagine cu mâncare. "
            "Identifică felul de mâncare, ingredientele principale și oferă o estimare aproximativă a caloriilor. "
            "Răspunde STRICT în format JSON cu cheile: "
            "{'food': '', 'ingredients': [], 'calories': 0}."
        )

    def _crop_plate(self, image: Image.Image):
        results = self.detector(image)
        boxes = results[0].boxes

        if len(boxes) == 0:
            return None

        PLATE_CLASSES = [41, 45]  # bowl, plate

        # Filtrăm doar farfuriile
        plate_boxes = [
            b for b in boxes
            if int(b.cls[0]) in PLATE_CLASSES
        ]

        if len(plate_boxes) == 0:
            return None

        # Alegem farfuria cu aria cea mai mare
        def area(b):
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            return (x2 - x1) * (y2 - y1)

        best = max(plate_boxes, key=area)

        x1, y1, x2, y2 = best.xyxy[0].tolist()
        return image.crop((x1, y1, x2, y2))

    def _ask_ollama(self, cropped_image: Image.Image):
        """Trimite farfuria decupată la Ollama pentru analiză."""

        # Convertim imaginea în base64
        cropped_image.save("debug_plate.png")
        print("DEBUG: imagine trimisă la Ollama salvată ca debug_plate.png")
        buf = io.BytesIO()
        cropped_image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        payload = {
            "model": self.ollama_model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": self._prompt(),
                    "images": [img_b64]
                }
            ],
            "options": {
                "temperature": 0.2,
                "num_predict": 150
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=200)
            data = response.json()

            # Extragem textul generat
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"]

            return json.dumps({"error": "Invalid response from Ollama"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def analyze(self, image: Image.Image):
        """Pipeline complet: YOLO detect → crop → fallback → Ollama → JSON final."""

        # 1️⃣ detectăm farfuria principală
        cropped = self._crop_plate(image)

        # 2️⃣ fallback: dacă YOLO nu găsește farfuria, trimitem întreaga imagine
        if cropped is None:
            print("⚠️ YOLO nu a detectat farfuria — trimit întreaga imagine la Ollama")
            cropped = image

        # 3️⃣ salvăm imaginea trimisă la Ollama pentru debug
        cropped.save("debug_plate.png")
        print("DEBUG: imagine trimisă la Ollama salvată ca debug_plate.png")

        # 4️⃣ trimitem farfuria la Ollama
        result = self._ask_ollama(cropped)

        # 5️⃣ returnăm JSON-ul final
        return result

    @staticmethod
    def _prompt() -> str:
        """Prompt strict pentru JSON valid."""
        return (
            "Analyze the food in the image and return ONLY a valid JSON object.\n"
            "Use STRICT JSON rules:\n"
            "- Only double quotes.\n"
            "- No comments.\n"
            "- No text outside JSON.\n"
            "Return exactly this structure:\n"
            "{\n"
            "  \"ingredients\": [\n"
            "      {\n"
            "          \"name\": \"ingredient_name\",\n"
            "          \"calories\": estimated_kcal,\n"
            "          \"protein\": grams_of_protein,\n"
            "          \"carbs\": grams_of_carbs,\n"
            "          \"fat\": grams_of_fat\n"
            "      }\n"
            "  ],\n"
            "  \"dish_name\": \"general category\",\n"
            "  \"total_calories\": total_kcal,\n"
            "  \"total_protein\": total_protein_grams,\n"
            "  \"total_carbs\": total_carbs_grams,\n"
            "  \"total_fat\": total_fat_grams\n"
            "}\n"
            "Be realistic with estimates. Output ONLY the JSON."
        )