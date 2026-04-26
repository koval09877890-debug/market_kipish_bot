import os
import asyncio
import requests
import google.generativeai as genai
from telegram import Bot

# Налаштування з Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TD_KEY = os.getenv("TWELVE_DATA_KEY")

# Налаштування Gemini 2.0 Flash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp') # Використовуємо 2.0 Flash

# Тикери для Twelve Data
SYMBOLS = "GOLD,GBP/USD,EUR/USD,AUD/USD,USD/JPY"

def get_twelve_data():
    try:
        url = f"https://api.twelvedata.com/quote?symbol={SYMBOLS}&apikey={TD_KEY}"
        response = requests.get(url).json()
        
        summary = "Поточні котирування (Twelve Data):\n"
        # Twelve Data повертає словник для декількох тикерів
        for symbol, data in response.items():
            price = data.get('close', 'Н/Д')
            change = data.get('percent_change', '0')
            summary += f"• {symbol}: {price} ({change}%)\n"
        return summary
    except Exception as e:
        return f"Помилка даних: {e}"

async def get_ai_analysis(market_info):
    prompt = (
        f"Ти — топовий трейдер Smart Money. Ось свіжі дані: {market_info}. "
        "Зроби жорсткий та швидкий аналіз для Telegram каналу. "
        "Акцент на GOLD та AUD/USD. Згадай можливі маніпуляції та пастки маркетмейкерів. "
        "Пиши українською, коротко, з вогняними емодзі."
    )
    response = model.generate_content(prompt)
    return response.text

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот 'Паравоз' на Gemini 2.0 та Twelve Data запущений!")
    
    while True:
        try:
            market_data = get_twelve_data()
            analysis = await get_ai_analysis(market_data)
            await bot.send_message(chat_id=CHANNEL_ID, text=analysis, parse_mode='Markdown')
            print("Аналіз відправлено в канал.")
            await asyncio.sleep(3600) # Чекаємо годину
        except Exception as e:
            print(f"Помилка в циклі: {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
