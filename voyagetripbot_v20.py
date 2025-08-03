
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)


BOT_TOKEN = '7209793844:AAHk1ilKgHRMbhbcDI1hZD7hFVowtYwHiR4'
ADMIN_CHAT_ID = 8207687995


LANGUAGE, NAME, PHONE, COUNTRY, DATE = range(5)
user_data = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Русский 🇷🇺', 'O‘zbekcha 🇺🇿', 'English 🇬🇧']]
    await update.message.reply_text(
        "Выберите язык / Tilni tanlang / Choose your language:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANGUAGE

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    user_data[update.effective_chat.id] = {'lang': lang}
    if "Русский" in lang:
        await update.message.reply_text("Пожалуйста, введите ваше имя:")
    elif "O‘zbekcha" in lang:
        await update.message.reply_text("Iltimos, ismingizni kiriting:")
    else:
        await update.message.reply_text("Please enter your name:")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['name'] = update.message.text
    lang = user_data[update.effective_chat.id]['lang']
    msg = {
        "Русский": "Введите ваш номер телефона:",
        "O‘zbekcha": "Telefon raqamingizni kiriting:",
    }.get(lang.split()[0], "Enter your phone number:")
    await update.message.reply_text(msg)
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['phone'] = update.message.text
    lang = user_data[update.effective_chat.id]['lang']
    msg = {
        "Русский": "Укажите страну, куда хотите поехать:",
        "O‘zbekcha": "Qaysi mamlakatga borishni xohlaysiz?",
    }.get(lang.split()[0], "Which country do you want to travel to?")
    await update.message.reply_text(msg)
    return COUNTRY

async def country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id]['country'] = update.message.text
    lang = user_data[update.effective_chat.id]['lang']
    msg = {
        "Русский": "Укажите предполагаемую дату поездки:",
        "O‘zbekcha": "Sayohat sanasini kiriting:",
    }.get(lang.split()[0], "Enter your intended travel date:")
    await update.message.reply_text(msg)
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id]['date'] = update.message.text
    data = user_data[chat_id]

    message = (
        f"📥 Новая заявка от клиента:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🌍 Страна: {data['country']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🌐 Язык: {data['lang']}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    await update.message.reply_text("✅ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Процесс отменён.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, country)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
