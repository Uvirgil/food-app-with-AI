import io
import base64
from openai import OpenAI
from PIL import Image


class VisionAnalyzer:
    def __init__(self, api_key: str):
        # Initializam clientul OpenAI folosind cheia API primita
        self.client = OpenAI(api_key=api_key)

    def analyze(self, image: Image.Image) -> str:
        # Convertim imaginea intr-un buffer in memorie
        buf = io.BytesIO()
        image.save(buf, format="PNG")

        # Extragem bytes din imagine
        img_bytes = buf.getvalue()

        # Convertim imaginea in Base64 pentru a o trimite catre API
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # Construim URL-ul inline pentru imagine (data URL)
        img_url = f"data:image/png;base64,{img_b64}"

        # Trimitem cererea catre modelul vizual GPT
        response = self.client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self._prompt(),  # promptul care cere JSON strict
                        },
                        {
                            "type": "input_image",
                            "image_url": img_url,  # imaginea codata Base64
                        },
                    ],
                }
            ],
        )

        # Returnam textul generat de model (ar trebui sa fie JSON strict)
        return response.output_text

    @staticmethod
    def _prompt() -> str:
        # Prompt trimis catre model pentru a forta un raspuns JSON strict
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