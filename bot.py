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
from downloader.engine import download_media


TEXTS = {
    "ar": {
        "choose_language": "🌐 اختر اللغة:",
        "changed": "✅ تم تغيير اللغة إلى العربية.",
        "welcome": (
            "🔥 HMB VIDEO DOWNLOADER PRO\n\n"
            "🔗 أرسل رابط الفيديو.\n\n"
            "ثم اختر نوع التحميل:\n\n"
            "🎬 VIDEO — فيديو\n"
            "🎵 Audio from Video — استخراج الصوت\n\n"
            "⚡ YouTube • TikTok • Instagram"
        ),
        "link_received": (
            "🔗 تم استلام الرابط.\n\n"
            "اختر نوع التحميل:"
        ),
        "invalid_url": "❌ الرجاء إرسال رابط صحيح.",
        "no_url": (
            "❌ لم يتم العثور على الرابط.\n"
            "أرسل الرابط مرة أخرى."
        ),
        "video_wait": (
            "🎬 VIDEO\n\n"
            "⏳ جارٍ تحميل الفيديو...\n"
            "⚡ يرجى الانتظار."
        ),
        "audio_wait": (
            "🎵 Audio from Video\n\n"
            "⏳ جارٍ استخراج الصوت...\n"
            "⚡ يرجى الانتظار."
        ),
        "cancelled": "❌ تم الإلغاء.",
        "error": (
            "❌ حدث خطأ أثناء التحميل.\n\n"
            "السبب:\n{error}"
        ),
        "help": (
            "📌 طريقة الاستخدام:\n\n"
            "1️⃣ أرسل رابط الفيديو\n"
            "2️⃣ اختر نوع التحميل\n"
            "3️⃣ انتظر حتى يكتمل التحميل\n\n"
            "🎬 VIDEO\n"
            "🎵 Audio from Video"
        ),
        "change_language": "🌐 تغيير اللغة",
    },

    "en": {
        "choose_language": "🌐 Choose your language:",
        "changed": "✅ Language changed to English.",
        "welcome": (
            "🔥 HMB VIDEO DOWNLOADER PRO\n\n"
            "🔗 Send a video link.\n\n"
            "Then choose the download type:\n\n"
            "🎬 VIDEO — Video\n"
            "🎵 Audio from Video — Extract audio\n\n"
            "⚡ YouTube • TikTok • Instagram"
        ),
        "link_received": (
            "🔗 Link received.\n\n"
            "Choose the download type:"
        ),
        "invalid_url": "❌ Please send a valid URL.",
        "no_url": (
            "❌ No link was found.\n"
            "Please send the link again."
        ),
        "video_wait": (
            "🎬 VIDEO\n\n"
            "⏳ Downloading video...\n"
            "⚡ Please wait."
        ),
        "audio_wait": (
            "🎵 Audio from Video\n\n"
            "⏳ Extracting audio...\n"
            "⚡ Please wait."
        ),
        "cancelled": "❌ Cancelled.",
        "error": (
            "❌ An error occurred while downloading.\n\n"
            "Reason:\n{error}"
        ),
        "help": (
            "📌 How to use:\n\n"
            "1️⃣ Send a video link\n"
            "2️⃣ Choose the download type\n"
            "3️⃣ Wait for the download to finish\n\n"
            "🎬 VIDEO\n"
            "🎵 Audio from Video"
        ),
        "change_language": "🌐 Change language",
    },
}


def get_lang(context):
    return context.user_data.get("language", "en")


def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🇸🇦 العربية",
                callback_data="lang_ar",
            ),
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en",
            ),
        ]
    ])


def menu(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎬 VIDEO",
                callback_data="video",
            ),
        ],
        [
            InlineKeyboardButton(
                "🎵 Audio from Video",
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


def language_button(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[lang]["change_language"],
                callback_data="change_language",
            )
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "language" not in context.user_data:
        await update.message.reply_text(
            TEXTS["en"]["choose_language"],
            reply_markup=language_keyboard(),
        )
        return

    lang = get_lang(context)

    await update.message.reply_text(
        TEXTS[lang]["welcome"],
        reply_markup=language_button(lang),
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    lang = get_lang(context)

    await update.message.reply_text(
        TEXTS[lang]["help"],
        reply_markup=language_button(lang),
    )


async def link_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    lang = get_lang(context)
    t = TEXTS[lang]

    url = "".join(update.message.text.split())

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(
            t["invalid_url"]
        )
        return

    context.user_data["url"] = url

    await update.message.reply_text(
        t["link_received"],
        reply_markup=menu(lang),
    )


async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Language: Arabic
    if data == "lang_ar":
        context.user_data["language"] = "ar"

        await query.edit_message_text(
            TEXTS["ar"]["changed"]
        )

        await query.message.reply_text(
            TEXTS["ar"]["welcome"],
            reply_markup=language_button("ar"),
        )
        return

    # Language: English
    if data == "lang_en":
        context.user_data["language"] = "en"

        await query.edit_message_text(
            TEXTS["en"]["changed"]
        )

        await query.message.reply_text(
            TEXTS["en"]["welcome"],
            reply_markup=language_button("en"),
        )
        return

    # Change language
    if data == "change_language":
        await query.edit_message_text(
            "🌐 Choose your language:",
            reply_markup=language_keyboard(),
        )
        return

    lang = get_lang(context)
    t = TEXTS[lang]

    # Cancel
    if data == "cancel":
        context.user_data.pop("url", None)

        await query.edit_message_text(
            t["cancelled"]
        )
        return

    # Get saved URL
    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text(
            t["no_url"]
        )
        return

    # Video
    if data == "video":
        await query.edit_message_text(
            t["video_wait"]
        )

    # MP3
    elif data == "mp3":
        await query.edit_message_text(
            t["audio_wait"]
        )

    else:
        return

    temp_dir = None

    try:
        filename, info, temp_dir = await asyncio.to_thread(
            download_media,
            url,
            data,
        )

        title = info.get(
            "title",
            "HMB Download",
        )

        with open(filename, "rb") as media:

            if data == "mp3":
                await query.message.reply_audio(
                    audio=media,
                    title=title[:64],
                    caption=(
                        "🎵 HMB VIDEO DOWNLOADER PRO\n\n"
                        f"🎶 {title}"
                    ),
                    read_timeout=300,
                    write_timeout=900,
                    connect_timeout=120,
                    pool_timeout=120,
                )

            else:
                await query.message.reply_video(
                    video=media,
                    caption=(
                        "🎬 HMB VIDEO DOWNLOADER PRO\n\n"
                        f"🎥 {title}"
                    ),
                    supports_streaming=True,
                    read_timeout=300,
                    write_timeout=900,
                    connect_timeout=120,
                    pool_timeout=120,
                )

        context.user_data.pop("url", None)

    except Exception as e:
        await query.message.reply_text(
            t["error"].format(
                error=str(e)[:1000]
            )
        )

    # IMPORTANT:
    # Do not call cleanup() here.
    # downloader/engine.py schedules cleanup after 5 minutes.


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

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler,
            pattern=(
                "^(video|mp3|cancel|"
                "lang_ar|lang_en|change_language)$"
            ),
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            link_handler,
        )
    )

    print(
        "🚀 HMB VIDEO DOWNLOADER PRO is running..."
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
