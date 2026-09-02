import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
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
        "link_received": "🔗 تم استلام الرابط.\n\nاختر نوع التحميل:",
        "invalid_url": "❌ الرجاء إرسال رابط صحيح.",
        "no_url": "❌ لم يتم العثور على الرابط.\nأرسل الرابط مرة أخرى.",
        "video_wait": "🎬 VIDEO\n\n⏳ جارٍ تحميل الفيديو...\n⚡ يرجى الانتظار.",
        "audio_wait": "🎵 Audio from Video\n\n⏳ جارٍ استخراج الصوت...\n⚡ يرجى الانتظار.",
        "cancelled": "❌ تم الإلغاء.",
        "error": "❌ حدث خطأ.\n\nالسبب:\n{error}",
        "help": (
            "📌 الأوامر:\n\n"
            "/start — بدء البوت\n"
            "/help — المساعدة\n"
            "/language — تغيير اللغة\n"
            "/decorate — زخرفة الاسم\n\n"
            "📥 أرسل رابط فيديو للتحميل."
        ),
        "change_language": "🌐 تغيير اللغة",
        "decorate_help": (
            "✨ زخرفة الاسم\n\n"
            "أرسل الاسم الذي تريد زخرفته.\n\n"
            "مثال:\n"
            "HONAR\n"
            "محمد"
        ),
        "decorated": "✨ زخارف اسمك:\n\n{names}",
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
        "link_received": "🔗 Link received.\n\nChoose the download type:",
        "invalid_url": "❌ Please send a valid URL.",
        "no_url": "❌ No link was found.\nPlease send the link again.",
        "video_wait": "🎬 VIDEO\n\n⏳ Downloading video...\n⚡ Please wait.",
        "audio_wait": "🎵 Audio from Video\n\n⏳ Extracting audio...\n⚡ Please wait.",
        "cancelled": "❌ Cancelled.",
        "error": "❌ An error occurred.\n\nReason:\n{error}",
        "help": (
            "📌 Commands:\n\n"
            "/start — Start the bot\n"
            "/help — Help\n"
            "/language — Change language\n"
            "/decorate — Name Decorator\n\n"
            "📥 Send a video link to download."
        ),
        "change_language": "🌐 Change language",
        "decorate_help": (
            "✨ Name Decorator\n\n"
            "Send the name you want to decorate.\n\n"
            "Example:\n"
            "HONAR\n"
            "محمد"
        ),
        "decorated": "✨ Your decorated names:\n\n{names}",
    },
}


def get_lang(context):
    return context.user_data.get("language", "en")


def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def menu(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 VIDEO", callback_data="video"),
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


def decorate_name(name):
    name = name.strip()

    if not name:
        return []

    return [
        f"『{name}』",
        f"꧁༺{name}༻꧂",
        f"『★ {name} ★』",
        f"乂 {name} 乂",
        f"ツ {name} ツ",
        f"亗 {name} 亗",
        f"彡 {name} 彡",
        f"♛ {name} ♛",
        f"★彡 {name} 彡★",
        f"༒ {name} ༒",
        f"☬ {name} ☬",
        f"𓆩 {name} 𓆪",
    ]


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


async def language_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🌐 Choose your language:",
        reply_markup=language_keyboard(),
    )


async def decorate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    lang = get_lang(context)

    await update.message.reply_text(
        TEXTS[lang]["decorate_help"]
    )

    context.user_data["waiting_for_name"] = True


async def link_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    lang = get_lang(context)
    t = TEXTS[lang]

    text = update.message.text.strip()

    # Name decorator
    if context.user_data.get("waiting_for_name"):
        context.user_data["waiting_for_name"] = False

        names = decorate_name(text)

        if not names:
            await update.message.reply_text(
                "❌ Please enter a name."
            )
            return

        result = "\n".join(
            f"{i}. {name}"
            for i, name in enumerate(names, 1)
        )

        await update.message.reply_text(
            t["decorated"].format(names=result)
        )
        return

    # Video URL
    url = "".join(text.split())

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

    if data == "change_language":
        await query.edit_message_text(
            "🌐 Choose your language:",
            reply_markup=language_keyboard(),
        )
        return

    lang = get_lang(context)
    t = TEXTS[lang]

    if data == "cancel":
        context.user_data.pop("url", None)

        await query.edit_message_text(
            t["cancelled"]
        )
        return

    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text(
            t["no_url"]
        )
        return

    if data == "video":
        await query.edit_message_text(
            t["video_wait"]
        )

    elif data == "mp3":
        await query.edit_message_text(
            t["audio_wait"]
        )

    else:
        return

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

    # cleanup لە downloader/engine.py ـە.
    # فایلەکە دوای 5 خولەک خۆکارانە دەسڕدرێتەوە.


async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start HMB Video Downloader"),
        BotCommand("help", "Help"),
        BotCommand("language", "Change language"),
        BotCommand("decorate", "Decorate a name"),
    ])


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(60)
        .read_timeout(120)
        .write_timeout(300)
        .pool_timeout(60)
        .post_init(post_init)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("language", language_command)
    )

    app.add_handler(
        CommandHandler("decorate", decorate_command)
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
