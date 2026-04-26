import os
import asyncio
import yfinance as yf
import google.generativeai as genai
from telegram import Bot

# Налаштування
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

genai.configure(api_key=GEMINI_KEY)

# Спроба підключити Gemini 3, якщо ні — ставимо 1.5
try:
    model = genai.GenerativeModel('gemini-3-flash')
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# Список активів (Золото та основні пари)
SYMBOLS = {
    "GC=F": "Gold (Золото)",
    "GBPUSD=X": "GBP/USD",
    "EURUSD=X": "EUR/USD",
    "AUDUSD=X": "AUD/USD",
    "JPY=X": "USD/JPY"
}

def get_market_data():
    try:
        summary = "📊 Дані з Yahoo Finance:\n"
        for ticker, name in SYMBOLS.items():
            data = yf.Ticker(ticker)
            price = data.fast_info['last_price']
            summary += f"• {name}: {price:.4f}\n"
        return summary
    except Exception as e:
        return f"Помилка Yahoo: {e}"

async def get_ai_analysis(market_info):
    prompt = (
        f"Ти профі Smart Money трейдер. Ось дані: {market_info}. "
        "Зроби жорсткий та короткий аналіз українською. "
        "Де ліквідність? Де пастка? Дай прогноз на найближчу годину з емодзі."
    )
    # Бот спробує видати аналіз
    response = model.generate_content(prompt)
    return response.text

async def main():
    bot = Bot(token=BOT_TOKEN)
    print(f"🚀 'Паравоз' на yfinance та Gemini запущений!")
    
    while True:
        try:
            market_data = get_market_data()
            analysis = await get_ai_analysis(market_data)
            
            await bot.send_message(chat_id=CHANNEL_ID, text=analysis)
            print("✅ Пост відправлено. Спимо годину.")
            
            # Пауза 1 година (можна спати спокійно)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"⚠️ Збій: {e}. Перезапуск через 10 хв.")
            await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
