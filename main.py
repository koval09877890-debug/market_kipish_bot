import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
import re
from datetime import datetime

# 🔑 Дані з Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

SYMBOLS = {
    "DX-Y.NYB": "US Dollar Index", 
    "GC=F": "Gold", 
    "GBPUSD=X": "GBP/USD", 
    "AUDUSD=X": "AUD/USD",
    "EURUSD=X": "EUR/USD"
}

def get_market_info():
    summary = f"⏰ ЧАС (Київ): {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    summary += "📊 РИНКОВІ ДАНІ:\n"
    for ticker, name in SYMBOLS.items():
        try:
            t = yf.Ticker(ticker)
            price = t.fast_info['last_price']
            fmt = ".2f" if "Index" in name else ".4f"
            summary += f"🔹 {name}: {price:{fmt}}\n"
        except:
            continue
    return summary

def run_kipish():
    print("🚀 Паравоз виїхав! Помилки з Markdown виправлено.")
    while True:
        try:
            if not CHANNEL_ID:
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            prompt = f"""
            Ти професійний Smart Money трейдер. 
            Дані ринку: {market_data}
            
            Твоє завдання:
            1. Проаналізуй структуру MS та силу DXY.
            2. Знайди найближчий FVG або локальний Order Block.
            3. ВАЖЛИВО: Став лімітки близько до поточної ціни (зона OTE 0.62-0.79).
            
            Формат відповіді (УКРАЇНСЬКОЮ):
            📊 КОНТЕКСТ РИНКУ
            🎯 АКТУАЛЬНІ ЛІМІТКИ (Entry, SL, TP)
            🚀 ЛОГІКА ВХОДУ (коротко)

            УВАГА: Не використовуй складне форматування Markdown, тільки жирний шрифт для заголовків.
            """
            
            response = model.generate_content(prompt)
            final_text = response.text

            try:
                # Намагаємося відправити з Markdown
                bot.send_message(CHANNEL_ID, final_text, parse_mode="Markdown")
            except:
                # Якщо Telegram "матюкається" на розмітку — відправляємо чистий текст
                bot.send_message(CHANNEL_ID, final_text)
                
            print(f"✅ СИГНАЛ ВІДПРАВЛЕНО: {datetime.now().strftime('%H:%M')}")
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
