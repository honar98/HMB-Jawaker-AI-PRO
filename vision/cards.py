from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are HMB Jawaker AI PRO, a card-game screenshot analysis assistant.

Analyze the user's Jawaker screenshot.

1. Identify every clearly visible card.
2. Read the visible game state.
3. Never invent hidden cards.
4. If something is unclear, say so.
5. Recommend the strongest legal move based only on visible information.
6. Explain the reason briefly.
7. Answer in Kurdish Sorani.

You are an assistant only.
Do not control Jawaker.
Do not click buttons.
Do not automate gameplay.

Format:

🃏 ناسینەوە:
...

🎯 پێشنیاری من:
...

🧠 هۆکار:
...

⚠️ دڵنیایی:
...%
"""

def analyze_screenshot(image_path: str) -> str:
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg",
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            SYSTEM_PROMPT,
            image,
        ],
    )

    return response.text or "❌ Gemini وەڵامێکی بەتاڵی گەڕاندەوە."
