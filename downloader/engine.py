import os
import subprocess
import tempfile
import threading
from pathlib import Path

import yt_dlp


CLEANUP_DELAY = 5 * 60  # 5 خولەک


def find_downloaded_file(folder):
    files = [
        p for p in Path(folder).glob("*")
        if p.is_file() and p.stat().st_size > 0
    ]

    if not files:
        raise RuntimeError("هیچ فایلێک دابەزی نەبوو.")

    return max(files, key=lambda p: p.stat().st_size)


def download_video(url: str, output_dir: str):
    output = os.path.join(
        output_dir,
        "%(title).80s.%(ext)s"
    )

    options = {
        "format": (
            "bestvideo[height<=1080]+bestaudio/"
            "best[height<=1080]/best"
        ),
        "outtmpl": output,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 5,
        "socket_timeout": 90,
        "http_chunk_size": 10485760,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    files = list(Path(output_dir).glob("*"))

    if not files:
        raise RuntimeError("فایلەکە نەدۆزرایەوە.")

    video_files = [
        p for p in files
        if p.suffix.lower() in (
            ".mp4", ".mkv", ".webm", ".mov"
        )
    ]

    if video_files:
        filename = str(max(
            video_files,
            key=lambda p: p.stat().st_size
        ))
    else:
        filename = str(find_downloaded_file(output_dir))

    return filename, info


def extract_mp3(video_file: str, output_dir: str, title: str):
    safe_title = "".join(
        c if c.isalnum() or c in " ._-()" else "_"
        for c in title
    ).strip()

    if not safe_title:
        safe_title = "HMB_Audio"

    output_file = os.path.join(
        output_dir,
        f"{safe_title[:80]}.mp3"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_file,
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        output_file,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg MP3 error: "
            + result.stderr[-1200:]
        )

    if not os.path.exists(output_file):
        raise RuntimeError("MP3 دروست نەکرا.")

    return output_file


def schedule_cleanup(temp_dir: str):
    """
    دوای 5 خولەک temp_dir بە تەواوی دەسڕێتەوە.
    """
    timer = threading.Timer(
        CLEANUP_DELAY,
        cleanup,
        args=(temp_dir,)
    )

    timer.daemon = True
    timer.start()


def download_media(url: str, mode: str):
    temp_dir = tempfile.mkdtemp(prefix="hmb_dl_")

    try:
        video_file, info = download_video(
            url,
            temp_dir,
        )

        title = info.get(
            "title",
            "HMB Download"
        )

        if mode == "mp3":
            mp3_file = extract_mp3(
                video_file,
                temp_dir,
                title,
            )

            schedule_cleanup(temp_dir)

            return mp3_file, info, temp_dir

        schedule_cleanup(temp_dir)

        return video_file, info, temp_dir

    except Exception:
        cleanup(temp_dir)
        raise


def cleanup(temp_dir: str):
    path = Path(temp_dir)

    if not path.exists():
        return

    for item in path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                cleanup(str(item))
        except OSError:
            pass

    try:
        path.rmdir()
    except OSError:
        pass
