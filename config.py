import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")
