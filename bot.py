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

    bold_upper = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    bold_lower = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"

    italic_upper = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    italic_lower = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"

    bold_italic_upper = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
    bold_italic_lower = "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"

    mono_upper = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    mono_lower = "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"

    double_upper = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
    double_lower = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"

    def convert(s, upper, lower):
        table = {}

        for a, b in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", upper):
            table[ord(a)] = b

        for a, b in zip("abcdefghijklmnopqrstuvwxyz", lower):
            table[ord(a)] = b

        return s.translate(table)

    def is_arabic(s):
        return any(
            "\u0600" <= c <= "\u06FF"
            or "\u0750" <= c <= "\u077F"
            or "\u08A0" <= c <= "\u08FF"
            for c in s
        )

    def arabic_style(s, mark):
        return "".join(
            c + mark if c not in " \n" else c
            for c in s
        )

    # Arabic names
    # Only decorate the letters themselves.
    if is_arabic(name):
        return [
            "مـحـمـد" if name == "محمد" else name.replace("", "ـ"),
            arabic_style(name, "\u0360"),
            arabic_style(name, "\u0337"),
            arabic_style(name, "\u0332"),
            arabic_style(name, "\u0305"),
            arabic_style(name, "\u035F"),
            f"『{name}』",
            f"【{name}】",
            f"《{name}》",
            f"﴿{name}﴾",
            f"٭ {name} ٭",
            f"۞ {name} ۞",
        ]

    # English names
    b = convert(name, bold_upper, bold_lower)
    i = convert(name, italic_upper, italic_lower)
    bi = convert(name, bold_italic_upper, bold_italic_lower)
    m = convert(name, mono_upper, mono_lower)
    d = convert(name, double_upper, double_lower)

    return [
        f"꧁༺ {bi} ༻꧂",
        f"𓆩♡𓆪 {i} 𓆩♡𓆪",
        f"『★』 {b} 『★』",
        f"♛『 {d} 』♛",
        f"亗〆 {m} 〆亗",
        f"乂⚡ {b} ⚡乂",
        f"彡★ {i} ★彡",
        f"『🔥 {bi} 🔥』",
        f"『💎 {d} 💎』",
        f"『👑 {b} 👑』",
        f"『⚡ {i} ⚡』",
        f"★彡[ {b} ]彡★",
        f"꧁𓊈𒆜 {d} 𒆜𓊉꧂",
        f"⚜️ {i} ⚜️",
        f"♕ {d} ♕",
        f"☬ {b} ☬",
        f"𒆜 {bi} 𒆜",
        f"𓆩 {i} 𓆪",
        f"『 {m} 』",
        f"【 {b} 】",
        f"〘 {d} 〙",
        f"《 {i} 》",
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
