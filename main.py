import os
import asyncio
import requests
import google.generativeai as genai
from telegram import Bot

# Налаштування з Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TD_KEY = os.getenv("TWELVE_DATA_KEY")

# Налаштування Gemini 3 Flash
genai.configure(api_key=GEMINI_KEY)
# Ставимо найновішу модель, яку ти бачиш у студії
model = genai.GenerativeModel('gemini-3-flash')

# Тикери для ринку
SYMBOLS = "GOLD,GBP/USD,EUR/USD,AUD/USD,USD/JPY"

def get_twelve_data():
    try:
        url = f"https://api.twelvedata.com/quote?symbol={SYMBOLS}&apikey={TD_KEY}"
        response = requests.get(url).json()
        summary = "📊 Поточні котирування:\n"
        if isinstance(response, dict):
            for symbol, data in response.items():
                price = data.get('close', 'Н/Д')
                summary += f"• {symbol}: {price}\n"
        return summary
    except Exception as e:
        return f"Помилка даних: {e}"

async def get_ai_analysis(market_info):
    prompt = (
        f"Ти — топовий трейдер Smart Money. Ось дані: {market_info}. "
        "Зроби розривний аналіз для Telegram. Акцент на пастках для ритейл-трейдерів. "
        "Пиши жорстко, по суті, українською, з вогняними емодзі. "
        "В кінці дай коротку пораду на наступну годину."
    )
    response = model.generate_content(prompt)
    return response.text

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("🚀 'Паравоз' на Gemini 3 Flash погнав!")
    
    while True:
        try:
            market_data = get_twelve_data()
            analysis = await get_ai_analysis(market_data)
            
            await bot.send_message(chat_id=CHANNEL_ID, text=analysis)
            print("✅ Аналіз відправлено!")
            
            # Пауза 1 година, щоб не палити ліміти Twelve Data дарма
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"⚠️ Тимчасовий збій: {e}")
            # Чекаємо 10 хв і пробуємо знову, якщо була помилка
            await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
