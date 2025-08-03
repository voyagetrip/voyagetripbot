
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

BOT_TOKEN = '7209793844:AAHk1ilKgHRMbhbcDI1hZD7hFVowtYwHiR4'
ADMIN_CHAT_ID = 8207687995

LANGUAGE, NAME, PHONE, COUNTRY, DATE = range(5)
user_data = {}

def start(update: Update, context: CallbackContext):
    reply_keyboard = [['Русский 🇷🇺', 'O‘zbekcha 🇺🇿', 'English 🇬🇧']]
    update.message.reply_text(
        "Выберите язык / Tilni tanlang / Choose your language:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return LANGUAGE

def language(update: Update, context: CallbackContext):
    lang = update.message.text
    user_data[update.message.chat_id] = {'lang': lang}
    if "Русский" in lang:
        update.message.reply_text("Пожалуйста, введите ваше имя:")
    elif "O‘zbekcha" in lang:
        update.message.reply_text("Iltimos, ismingizni kiriting:")
    else:
        update.message.reply_text("Please enter your name:")
    return NAME

def name(update: Update, context: CallbackContext):
    user_data[update.message.chat_id]['name'] = update.message.text
    lang = user_data[update.message.chat_id]['lang']
    if "Русский" in lang:
        update.message.reply_text("Введите ваш номер телефона:")
    elif "O‘zbekcha" in lang:
        update.message.reply_text("Telefon raqamingizni kiriting:")
    else:
        update.message.reply_text("Enter your phone number:")
    return PHONE

def phone(update: Update, context: CallbackContext):
    user_data[update.message.chat_id]['phone'] = update.message.text
    lang = user_data[update.message.chat_id]['lang']
    if "Русский" in lang:
        update.message.reply_text("Укажите страну, куда хотите поехать:")
    elif "O‘zbekcha" in lang:
        update.message.reply_text("Qaysi mamlakatga borishni xohlaysiz?")
    else:
        update.message.reply_text("Which country do you want to travel to?")
    return COUNTRY

def country(update: Update, context: CallbackContext):
    user_data[update.message.chat_id]['country'] = update.message.text
    lang = user_data[update.message.chat_id]['lang']
    if "Русский" in lang:
        update.message.reply_text("Укажите предполагаемую дату поездки:")
    elif "O‘zbekcha" in lang:
        update.message.reply_text("Sayohat sanasini kiriting:")
    else:
        update.message.reply_text("Enter your intended travel date:")
    return DATE

def date(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
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

    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    update.message.reply_text("✅ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Процесс отменён.")
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, language)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
