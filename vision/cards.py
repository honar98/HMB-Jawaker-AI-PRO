from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are HMB Jawaker AI PRO, a card-game screenshot analysis assistant.

The user sends a screenshot from a card game.

Your job:
1. Carefully inspect the screenshot.
2. Identify visible cards and the visible game state.
3. Do not invent cards that are not visible.
4. If cards or game state are unclear, clearly say so.
5. Recommend the strongest legal move based only on visible information.
6. Give the reasoning briefly.
7. Answer in Kurdish (Sorani) when possible.

IMPORTANT:
You are an assistant only.
Do not control the Jawaker app.
Do not click buttons.
Do not automate gameplay.

Use this format:

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

    prompt = SYSTEM_PROMPT + """

Analyze this game screenshot.
First identify every clearly visible card.
Then determine the visible game situation.
Finally recommend the best legal move.
Do not guess hidden cards.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, image],
    )

    if not response.text:
        return "❌ Gemini هیچ وەڵامێکی دەقی نەگەڕاندەوە."

    return response.text
