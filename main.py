import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime

# 🔑 Налаштування (Railway Variables)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# Повертаємо ініціалізацію, яка працювала
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview') # Залишаємо Gemini 3

bot = telebot.TeleBot(BOT_TOKEN)

SYMBOLS = {
    "DX-Y.NYB": "DXY (Індекс долара)", 
    "GC=F": "Gold (Золото)", 
    "GBPUSD=X": "GBP/USD", 
    "EURUSD=X": "EUR/USD",
    "AUDUSD=X": "AUD/USD (Озі)"
}

def get_market_info():
    summary = f"⏰ ЧАС: {datetime.now().strftime('%d.%m %H:%M')} (Kyiv)\n\n"
    market_context = ""
    for ticker, name in SYMBOLS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="5d")
            if hist.empty: continue
            curr = hist['Close'].iloc[-1]
            high = hist['High'].iloc[-1]
            low = hist['Low'].iloc[-1]
            # Форматування для стабільності
            fmt = ".2f" if any(x in name for x in ["Index", "Gold"]) else ".4f"
            summary += f"🔹 **{name}**: `{curr:{fmt}}`\n"
            market_context += f"{name}: Зараз {curr:{fmt}}, High: {high:{fmt}}, Low: {low:{fmt}}. "
        except Exception as e:
            print(f"Помилка даних {ticker}: {e}")
    return summary, market_context

def run_kipish():
    # Текст запуску, як на твоєму скріні
    print("🚀 Робот на Gemini 3 (Forex + AUD/USD) у роботі...") 
    while True:
        try:
            stats_text, ai_context = get_market_info()
            
            prompt = f"""
            Ти — Senior Smart Money Трейдер. Проаналізуй КОЖЕН актив окремо:
            {ai_context}
            
            Для КОЖНОГО (Gold, GBP/USD, EUR/USD, AUD/USD) дай:
            - Напрямок (Bias)
            - POI (Зона входу ближче до поточної ціни)
            - Take Profit
            
            Важливо: НЕ використовуй нижні підкреслення '_' у тексті, тільки зірочки '**' для жирного тексту.
            Відповідай українською, професійно.
            """
            
            response = model.generate_content(prompt)
            # Додаємо префікс аналізу
            full_message = f"{stats_text}\n📊 **АНАЛІЗ ТА ЛІМІТКИ (GEMINI 3)**\n\n{response.text}"
            
            # Використовуємо Markdown (без V2), щоб уникнути помилок парсингу
            bot.send_message(CHANNEL_ID, full_message, parse_mode="Markdown")
            print(f"✅ Сигнал відправлено о {datetime.now().strftime('%H:%M')}")
            
            time.sleep(7200) # Пауза 2 години
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            # Якщо це помилка парсингу, пробуємо відправити без розмітки
            if "can't parse entities" in str(e).lower():
                bot.send_message(CHANNEL_ID, full_message)
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
