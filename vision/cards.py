import base64
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are HMB Jawaker AI PRO, a game-analysis assistant.

The user sends a screenshot from a card game.

Your job:
1. Carefully inspect the screenshot.
2. Identify visible cards and game state when possible.
3. Do not invent cards that are not visible.
4. Explain uncertainty if the screenshot is unclear.
5. Recommend the strongest legal move based only on visible information.
6. Keep the answer concise and useful.

IMPORTANT:
You are an assistant only.
Do not control the Jawaker app.
Do not click buttons.
Do not automate gameplay.

Answer in Kurdish when possible.

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

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze this game screenshot and "
                            "recommend the best legal move."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/jpeg;base64,{image_b64}"
                        ),
                    },
                ],
            },
        ],
    )

    return response.output_text
