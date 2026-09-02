import os
import json
import time
from pathlib import Path

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

MEMORY_DIR = Path("data/game_memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = r"""
You are HMB Jawaker AI PRO MAX — a UNIVERSAL CARD-GAME ANALYSIS AI.

Your job is to analyze card-game screenshots and maintain useful
memory of the SAME GAME across multiple screenshots.

You are NOT a gameplay automation bot.
You only analyze screenshots and recommend legal moves.

========================
CORE ABILITIES
========================

1. Detect the card game automatically.
2. Recognize visible cards.
3. Track the user's visible hand.
4. Track cards played/discarded when visible.
5. Track opponents and visible actions.
6. Track score, round, turn, melds and tricks when visible.
7. Remember information from previous screenshots of the same session.
8. Detect when the game state changes.
9. Remove cards from the user's hand when they are visibly played.
10. Add newly received cards when visible.
11. Keep a history of important cards and actions.
12. Use previous visible information to make better recommendations.

========================
CARD MEMORY
========================

Maintain these concepts:

USER_HAND
CARDS_PLAYED
CARDS_DISCARDED
VISIBLE_OPPONENT_ACTIONS
CURRENT_TABLE
SCORE
ROUND
TURN
TRUMP
MELDS
TRICKS
GAME_TYPE

Never invent hidden cards.

If a card was previously visible and later disappears,
do NOT automatically assume where it went unless the screenshot
provides enough evidence.

========================
OPPONENT ANALYSIS
========================

Use only visible evidence.

For each opponent, track when possible:
- cards they visibly played
- cards they visibly discarded
- cards they picked up if visible
- suits/ranks they appear interested in
- visible melds
- visible scoring information

Then estimate which cards may be useful to them.

IMPORTANT:
These are estimates, NOT hidden-card knowledge.

========================
DISCARD ANALYSIS
========================

When the user needs to choose a card to discard/free:

Evaluate every visible candidate.

Prefer cards that:
- have low value to the user's current strategy
- are not important to likely melds
- are less useful to opponents based on visible history
- reduce future risk
- do not break a strong combination
- do not unnecessarily reveal useful information

Protect cards that:
- complete or nearly complete strong combinations
- have strong future potential
- are strategically important
- are less risky to keep

If opponent information is insufficient, say so.

========================
SELF-CHECK
========================

Before responding:

1. Re-check the game type.
2. Re-check the visible cards.
3. Compare with previous session memory.
4. Check the recommended move is legal.
5. Check that the card actually exists in the user's visible hand.
6. Check that no hidden information was invented.
7. Check whether an opponent could benefit from the discarded card.
8. Lower confidence if the screenshot is unclear.

Do NOT expose private chain-of-thought.

========================
OUTPUT
========================

🎮 یاری:
...

🧠 دۆخی ئێستا:
...

🃏 کارتەکانی من:
...

👥 شیکاری بەرامبەر:
...

🎯 باشترین هەنگاو:
...

🗑️ ئەگەر فڕێدانە:
...

🛡️ بۆچی ئەمە باشترە:
...

⚠️ مەترسی:
...

📈 دڵنیایی:
...%

Answer in Kurdish (Sorani) whenever possible.
"""

def memory_file(session_id):
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(session_id))
    return MEMORY_DIR / f"{safe_id}.json"

def load_memory(session_id):
    path = memory_file(session_id)

    if not path.exists():
        return {
            "created": time.time(),
            "game": None,
            "screenshots": 0,
            "history": []
        }

    try:
        return json.loads(path.read_text())
    except Exception:
        return {
            "created": time.time(),
            "game": None,
            "screenshots": 0,
            "history": []
        }

def save_memory(session_id, memory):
    path = memory_file(session_id)

    # Keep memory useful but prevent unlimited growth.
    memory["history"] = memory.get("history", [])[-15:]

    path.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2)
    )

def analyze_screenshot(image_path: str, session_id="default") -> str:
    if not os.path.exists(image_path):
        return "❌ وێنەکە نەدۆزرایەوە."

    memory = load_memory(session_id)
    memory["screenshots"] = memory.get("screenshots", 0) + 1

    previous_history = memory.get("history", [])

    memory_context = json.dumps(
        {
            "game": memory.get("game"),
            "screenshots_analyzed": memory.get("screenshots"),
            "previous_observations": previous_history[-10:]
        },
        ensure_ascii=False
    )

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg",
    )

    prompt = SYSTEM_PROMPT + f"""

========================
PREVIOUS GAME MEMORY
========================

{memory_context}

Use this memory only as previous OBSERVED information.

Now analyze the new screenshot.

Return:
1. Game identification
2. Current visible state
3. Updated visible card information
4. Opponent observations
5. Best legal move
6. Best discard if applicable
7. Risk
8. Confidence

At the END add this machine-readable section:

<MEMORY_UPDATE>
{{
  "game": "detected game",
  "user_hand": [],
  "cards_played": [],
  "cards_discarded": [],
  "opponents": [],
  "score": "",
  "round": "",
  "turn": "",
  "trump": "",
  "important_notes": []
}}
</MEMORY_UPDATE>

Only put information actually supported by the screenshot
or previous observed memory.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            temperature=0.15,
            max_output_tokens=1600,
        ),
    )

    text = getattr(response, "text", None)

    if not text:
        return "❌ Gemini هیچ وەڵامێکی دەقی نەگەڕاندەوە."

    text = text.strip()

    # Extract and hide internal memory data.
    if "<MEMORY_UPDATE>" in text:
        visible_text = text.split("<MEMORY_UPDATE>", 1)[0].strip()

        try:
            block = text.split("<MEMORY_UPDATE>", 1)[1]

            if "</MEMORY_UPDATE>" in block:
                block = block.split("</MEMORY_UPDATE>", 1)[0].strip()

            # Remove optional markdown JSON fences.
            block = block.replace("```json", "").replace("```", "").strip()

            update = json.loads(block)

            memory["game"] = update.get("game", memory.get("game"))
            memory["history"].append({
                "time": time.time(),
                "game": update.get("game"),
                "user_hand": update.get("user_hand", []),
                "cards_played": update.get("cards_played", []),
                "cards_discarded": update.get("cards_discarded", []),
                "opponents": update.get("opponents", []),
                "score": update.get("score", ""),
                "round": update.get("round", ""),
                "turn": update.get("turn", ""),
                "trump": update.get("trump", ""),
                "important_notes": update.get("important_notes", [])
            })

            save_memory(session_id, memory)

        except Exception:
            pass

        # NEVER expose internal memory data to the user.
        text = visible_text

    # Safety cleanup in case the model returns internal tags incorrectly.
    text = text.replace("<MEMORY_UPDATE>", "")
    text = text.replace("</MEMORY_UPDATE>", "")
    text = text.replace("```json", "")
    text = text.replace("```", "")

    return text.strip()
