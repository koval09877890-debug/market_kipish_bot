import os
import time
import requests
import yfinance as yf
import google.generativeai as genai
from telegram import Bot
import asyncio

# Налаштування ключів з Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID") # ID твого каналу

# Ініціалізація ШІ
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Список пар для моніторингу
SYMBOLS = {
    "GOLD": "GC=F",
    "GBP/USD": "GBPUSD=X",
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "JPY=X"
}

def get_market_data():
    summary = ""
    for name, ticker in SYMBOLS.items():
        data = yf.Ticker(ticker).history(period="1d", interval="1h")
        if not data.empty:
            last_price = data['Close'].iloc[-1]
            change = data['Close'].iloc[-1] - data['Open'].iloc[-1]
            summary += f"{name}: {round(last_price, 4)} (Зміна: {round(change, 4)})\n"
    return summary

async def get_ai_analysis(market_info):
    prompt = f"""
    Ти — професійний трейдер та аналітик Smart Money. 
    Ось поточні ціни на ринку:
    {market_info}
    
    Твоє завдання:
    1. Проаналізуй ці рухи. 
    2. Врахуй глобальний кіпіш (геополітику, новини, Polymarket).
    3. Знайди потенційні "пастки" (Stop Hunt) для роздрібних трейдерів.
    4. Напиши короткий звіт для каналу в стилі "Market Intelligence".
    
    Використовуй емодзі, пиши по-простому, але професійно. Акцентуй на GOLD та AUD/USD.
    """
    response = model.generate_content(prompt)
    return response.text

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот запущений...")
    
    while True:
        try:
            market_info = get_market_data()
            analysis = await get_ai_analysis(market_info)
            
            await bot.send_message(chat_id=CHANNEL_ID, text=analysis)
            print("Звіт відправлено в канал.")
            
            # Чекаємо 1 годину (3600 секунд)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Помилка: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
