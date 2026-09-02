import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from downloader.engine import download_media, cleanup


def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 VIDEO", callback_data="video"),
        ],
        [
            InlineKeyboardButton(
                "🎵 دەنگی سەر ڤیدیۆ",
                callback_data="mp3",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel",
            ),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🔥 HMB VIDEO DOWNLOADER PRO

🔗 لینکەکەی ڤیدیۆ بنێرە.

پاشان هەڵبژێرە:

🎬 VIDEO — ڤیدیۆ
🎵 دەنگی سەر ڤیدیۆ — MP3
🎶 گۆرانیی تەواو — ناسینەوەی گۆرانی

⚡ YouTube • TikTok • Instagram"""
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """📌 بەکارهێنان:

1️⃣ لینک بنێرە
2️⃣ جۆری دابەزاندن هەڵبژێرە
3️⃣ چاوەڕێ بکە

🎬 VIDEO
🎵 دەنگی سەر ڤیدیۆ
🎶 گۆرانیی تەواو"""
    )


async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "".join(update.message.text.split())

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(
            "❌ تکایە لینکێکی دروست بنێرە."
        )
        return

    context.user_data["url"] = url

    await update.message.reply_text(
        "🔗 لینک وەرگیرا.\n\n"
        "جۆری دابەزاندن هەڵبژێرە:",
        reply_markup=menu(),
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mode = query.data

    if mode == "cancel":
        context.user_data.pop("url", None)
        await query.edit_message_text("❌ هەڵوەشێنرایەوە.")
        return

    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text(
            "❌ لینک نەدۆزرایەوە.\n"
            "دووبارە لینکەکە بنێرە."
        )
        return

    if mode == "video":
        await query.edit_message_text(
            """🎬 VIDEO

⏳ ڤیدیۆکە دابەزێت...
⚡ تکایە چاوەڕێ بکە."""
        )

    elif mode == "mp3":
        await query.edit_message_text(
            """🎵 دەنگی سەر ڤیدیۆ

⏳ دەنگەکە لە ڤیدیۆکە جیا دەکرێتەوە...
⚡ تکایە چاوەڕێ بکە."""
        )

    temp_dir = None

    try:
        # VIDEO / MP3
        if mode in ("video", "mp3"):
            filename, info, temp_dir = await asyncio.to_thread(
                download_media,
                url,
                mode,
            )

            title = info.get("title", "HMB Download")

            with open(filename, "rb") as media:
                if mode == "mp3":
                    await query.message.reply_audio(
                        audio=media,
                        title=title[:64],
                        caption=(
                            "🎵 HMB VIDEO DOWNLOADER PRO\n\n"
                            f"🎶 {title}"
                        ),
                    )
                else:
                    await query.message.reply_video(
                        video=media,
                        caption=(
                            "🎬 HMB VIDEO DOWNLOADER PRO\n\n"
                            f"🎥 {title}"
                        ),
                        supports_streaming=True,
                    )

            context.user_data.pop("url", None)
            return

    finally:
        if temp_dir:
            cleanup(temp_dir)


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(60)
        .read_timeout(120)
        .write_timeout(300)
        .pool_timeout(60)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        CallbackQueryHandler(
            callback_handler,
            pattern="^(video|mp3|cancel)$",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            link_handler,
        )
    )

    print("🚀 HMB VIDEO DOWNLOADER PRO is running...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
