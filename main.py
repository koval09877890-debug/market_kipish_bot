import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time

# 🔑 Дані з Railway Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID') # Твій канал -100...

# 🤖 Налаштування Gemini (як у футбольному)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

# Список активів для Yahoo Finance
SYMBOLS = {
    "GC=F": "Золото (GOLD)",
    "GBPUSD=X": "GBP/USD",
    "EURUSD=X": "EUR/USD",
    "AUDUSD=X": "AUD/USD",
    "JPY=X": "USD/JPY"
}

def get_market_info():
    try:
        summary = "📊 СТАН РИНКУ НА ЗАРАЗ:\n\n"
        for ticker, name in SYMBOLS.items():
            t = yf.Ticker(ticker)
            # Беремо останню ціну
            price = t.fast_info['last_price']
            summary += f"🔹 {name}: {price:.4f}\n"
        return summary
    except Exception as e:
        return f"❌ Помилка Yahoo: {str(e)[:50]}"

def ask_gemini_market(data):
    prompt = (
        f"Ти — професійний трейдер Smart Money. Проаналізуй ці дані: {data}. "
        "Напиши короткий кіпіш-аналіз для Telegram каналу. "
        "Де пастки маркетмейкерів? Де ліквідність? Дай прогноз на годину. "
        "Пиши УКРАЇНСЬКОЮ мовою, жорстко, по суті, з вогняними емодзі."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Помилка AI: {str(e)[:50]}"

def run_kipish():
    print("🚀 'Паравоз' виїхав на колію!")
    while True:
        try:
            # 1. Отримуємо цифри
            market_data = get_market_info()
            # 2. Питаємо у Gemini
            analysis = ask_gemini_market(market_data)
            # 3. Відправляємо в канал
            bot.send_message(CHANNEL_ID, analysis)
            print("✅ Сигнал відправлено в канал!")
            # 4. Спимо 1 годину (3600 секунд)
            time.sleep(3600)
        except Exception as e:
            print(f"❌ Помилка в циклі: {e}")
            time.sleep(300) # Якщо помилка — чекаємо 5 хв і пробуємо знову

if __name__ == "__main__":
    run_kipish()
