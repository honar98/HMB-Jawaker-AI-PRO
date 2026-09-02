import os
import tempfile

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from vision.cards import analyze_screenshot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 HMB Jawaker AI PRO\n\n"
        "📸 Screenshot ـی یاری بنێرە.\n"
        "🔍 AI وێنەکە شیکاری دەکات.\n"
        "🎯 پێشنیاری هەنگاوی باشتر دەدات.\n\n"
        "⚡ PRO AI Assistant Ready"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 بەکارهێنان:\n\n"
        "/start — دەستپێکردن\n"
        "/help — یارمەتی\n\n"
        "📸 Screenshot بنێرە بۆ شیکردنەوە."
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    status = await message.reply_text(
        "🔍 Screenshot وەردەگیرێت...\n"
        "🧠 AI لەسەری کار دەکات..."
    )

    photo = message.photo[-1]
    telegram_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    ) as temp:
        image_path = temp.name

    try:
        await telegram_file.download_to_drive(image_path)

        result = analyze_screenshot(image_path, session_id=str(update.effective_chat.id))

        await status.edit_text(
            "🧠 HMB Jawaker AI PRO\n\n"
            + result
        )

    except Exception as e:
        await status.edit_text(
            "❌ هەڵەیەک ڕوویدا.\n\n"
            f"{str(e)[:800]}"
        )

    finally:
        try:
            os.remove(image_path)
        except OSError:
            pass


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )

    print("🚀 HMB Jawaker AI PRO is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
