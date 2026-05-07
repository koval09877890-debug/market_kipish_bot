import telebot
import os
from genai import Client # Новий спосіб імпорту
import yfinance as yf
import time
from datetime import datetime

# 🔑 Налаштування (Railway Variables)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# Ініціалізація нового клієнта Google AI
client = Client(api_key=GEMINI_KEY)
MODEL_ID = "gemini-3-flash-preview" # Твоя модель з вибору

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
            summary += f"🔹 **{name}**: `{curr:.4f}`\n"
            market_context += f"{name}: Зараз {curr:.4f}, High: {high:.4f}, Low: {low:.4f}. "
        except Exception as e:
            print(f"Помилка даних {ticker}: {e}")
    return summary, market_context

def run_kipish():
    print(f"🚀 Робот на НОВОМУ SDK (Gemini 3 Flash) запущений...")
    while True:
        try:
            stats_text, ai_context = get_market_info()
            
            prompt = f"""
            Ти — Senior Smart Money Трейдер. Проаналізуй КОЖЕН актив окремо:
            {ai_context}
            
            Для кожного (Gold, GBP/USD, EUR/USD, AUD/USD) дай:
            - Напрямок (Bias)
            - Точку входу (найближча зона OB/FVG на M15)
            - Take Profit
            Пиши коротко, професійно, українською.
            """
            
            # Новий спосіб виклику генерації
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            
            full_message = f"{stats_text}\n📊 **АНАЛІЗ (НОВИЙ SDK)**\n\n{response.text}"
            bot.send_message(CHANNEL_ID, full_message, parse_mode="Markdown")
            
            time.sleep(7200) # Пауза 2 години
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
