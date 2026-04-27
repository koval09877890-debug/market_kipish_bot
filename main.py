import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time

# 🔑 Беремо дані з Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
# Отримуємо ID каналу
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# Перевірка в логах (ти побачиш це в Railway)
print(f"DEBUG: Мій токен: {BOT_TOKEN[:5] if BOT_TOKEN else 'НЕМАЄ'}...")
print(f"DEBUG: ID каналу: {CHANNEL_ID}")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

SYMBOLS = {"GC=F": "Gold", "GBPUSD=X": "GBP/USD", "AUDUSD=X": "AUD/USD"}

def get_market_info():
    summary = "📊 РИНОК:\n"
    for ticker, name in SYMBOLS.items():
        try:
            t = yf.Ticker(ticker)
            price = t.fast_info['last_price']
            summary += f"🔹 {name}: {price:.4f}\n"
        except:
            continue
    return summary

def run_kipish():
    print("🚀 Паравоз виїхав!")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ ПОМИЛКА: CHANNEL_ID не знайдено в Variables!")
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            response = model.generate_content(f"Ти Smart Money трейдер. Дані: {market_data}. Напиши аналіз укр мовою з емодзі.")
            
            # ВІДПРАВКА
            bot.send_message(CHANNEL_ID, response.text)
            print("✅ СИГНАЛ В КАНАЛІ!")
            time.sleep(3600)
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
