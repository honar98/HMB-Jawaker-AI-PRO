import os
import subprocess
import tempfile
import requests
from urllib.parse import quote

from config import BASE_DIR


AUDD_URL = "https://api.audd.io/"


def make_sample(audio_file):
    sample = os.path.join(
        tempfile.gettempdir(),
        "hmb_music_sample.mp3"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", audio_file,
        "-t", "30",
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "64k",
        sample,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg error:\n" + result.stderr[-800:]
        )

    return sample


def recognize_music(audio_file):
    token = os.getenv("AUDD_API_TOKEN")

    if not token:
        raise RuntimeError(
            "AUDD_API_TOKEN نەدۆزرایەوە."
        )

    sample = make_sample(audio_file)

    try:
        with open(sample, "rb") as audio:
            response = requests.post(
                AUDD_URL,
                data={
                    "api_token": token,
                    "return": "apple_music,spotify",
                    "market": "IQ",
                },
                files={
                    "file": audio,
                },
                timeout=90,
            )

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"AudD error: {data.get('error')}"
            )

        return data.get("result")

    finally:
        try:
            os.remove(sample)
        except OSError:
            pass


def yt_music_search_url(artist, title):
    query = f"{artist} {title}"
    return (
        "https://music.youtube.com/search?q="
        + quote(query)
    )
