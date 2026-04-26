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
# Пробуємо повний шлях до моделі, як це зазвичай працює в API
model = genai.GenerativeModel('models/gemini-2.0-flash-exp')

# Тикери для Twelve Data (валюти та золото)
SYMBOLS = "GOLD,GBP/USD,EUR/USD,AUD/USD,USD/JPY"

def get_twelve_data():
    try:
        url = f"https://api.twelvedata.com/quote?symbol={SYMBOLS}&apikey={TD_KEY}"
        response = requests.get(url).json()
        
        summary = "Дані ринку (Twelve Data):\n"
        # Перевірка на успішну відповідь (Twelve Data повертає словник при декількох символах)
        if isinstance(response, dict):
            for symbol, data in response.items():
                price = data.get('close', 'Н/Д')
                change = data.get('percent_change', '0')
                summary += f"• {symbol}: {price} ({change}%)\n"
        return summary
    except Exception as e:
        return f"Технічна пауза в даних: {e}"

async def get_ai_analysis(market_info):
    # Промпт під твій стиль Smart Money
    prompt = (
        f"Ти — експерт Smart Money. Ось свіжі цифри: {market_info}. "
        "Зроби короткий, але жорсткий аналіз для Telegram. "
        "Акцент на GOLD та AUD/USD. Розкажи про можливі пастки маркетмейкерів (Stop Hunt). "
        "Пиши українською, з вогняними емодзі, стисло і по ділу."
    )
    response = model.generate_content(prompt)
    return response.text

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот 'Паравоз' на Gemini 2.0 та Twelve Data успішно запущений!")
    
    while True:
        try:
            market_data = get_twelve_data()
            analysis = await get_ai_analysis(market_data)
            # Відправка повідомлення в канал
            await bot.send_message(chat_id=CHANNEL_ID, text=analysis, parse_mode='Markdown')
            print("Сигнал відправлено в канал.")
            
            # Чекаємо 1 годину (3600 секунд) до наступного аналізу
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Помилка в циклі: {e}")
            # Якщо сталась помилка (наприклад, ліміт API), чекаємо 5 хвилин і пробуємо знову
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
