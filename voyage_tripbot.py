from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

def normalize_hotel_data(data):
    for country in data.values():
        for city in country.values():
            for star in ["3", "4", "5"]:
                city.setdefault(star, [])
    return data

hotels = normalize_hotel_data({
    "Турция": {
        "Анталия": {
            "3": ["Lara Garden Hotel", "Oscar Boutique Hotel"],
            "4": ["Best Western Plus Khan Hotel", "Akra V Hotel"],
            "5": ["Rixos Premium Belek", "Delphin Imperial Lara"]
        },
        "Стамбул": {
            "3": ["Hotel Sapphire"],
            "4": ["Radisson Blu Hotel Istanbul"],
            "5": ["Swissôtel The Bosphorus"]
        }
    },
    "ОАЭ": {
        "Дубай": {
            "3": ["Rove Downtown"],
            "4": ["Citymax Hotel Bur Dubai"],
            "5": ["Atlantis The Palm"]
        }
    }
})

ASK_NAME, ASK_PHONE, ASK_DATES = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(country, callback_data=country)] for country in hotels]
    await update.message.reply_text("✈️ Выберите страну:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    parts = data.split("|")
    if len(parts) == 1:
        country = parts[0]
        context.user_data["country"] = country
        cities = hotels[country]
        keyboard = [[InlineKeyboardButton(city, callback_data=f"{country}|{city}")] for city in cities]
        await query.edit_message_text(f"🌍 {country}\n📍 Выберите город:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif len(parts) == 2:
        country, city = parts
        context.user_data["city"] = city
        stars = hotels[country][city]
        keyboard = [[InlineKeyboardButton(f"{s} ⭐", callback_data=f"{country}|{city}|{s}")] for s in stars]
        await query.edit_message_text(f"📍 {city}\n⭐ Выберите категорию отеля:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif len(parts) == 3:
        country, city, star = parts
        context.user_data.update({"country": country, "city": city, "stars": star})
        hotel_list = hotels[country][city][star]
        context.user_data["hotels"] = hotel_list
        text = f"📍 Город: {city}⭐ Категория: {star} звёзд"
        for h in hotel_list:
            text += f"🏨 {h}💰 от ... / ночь ℹ️ Цена зависит от сезона"
        text += "📝 Чтобы оставить заявку, введите команду: /book"
        await query.edit_message_text(text)

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Введите ваше имя:")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Введите ваш номер телефона:")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📅 Укажите даты поездки:")
    return ASK_DATES

async def get_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dates"] = update.message.text
    user = context.user_data
    selected_hotel = user["hotels"][0] if user.get("hotels") else "-"
message = (
    f"🚀 Новая заявка!\n\n"
   f"Имя: {context.user_data['name']}\n"
    f"Телефон: {context.user_data['phone']}\n"
    f"Даты поездки: {context.user_data['dates']}\n"
    f"Страна: {context.user_data['country']}\n"
    f"Город: {context.user_data['city']}\n"
    f"Категория: {context.user_data['stars']}\n"
    f"Предпочтительный отель: {context.user_data['hotel']}\n"
)

async def get_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
    await context.bot.send_message(chat_id='@voyagetrip', text=message)
    await update.message.reply_text("✅ Спасибо! Мы свяжемся с вами в ближайшее время.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token("7209793844:AAHk1ilKgHRMbhbcDI1hZD7hFVowtYwHiR4").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("book", book)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dates)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    print("✅ Бот запущен")
    app.run_polling()
