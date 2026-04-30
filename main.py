import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime, timedelta

# 🔑 Дані з Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

# Список символів (Додав коректні тікери для фунта та євро)
SYMBOLS = {
    "DX-Y.NYB": "US Dollar Index", 
    "GC=F": "Gold", 
    "GBPUSD=X": "GBP/USD", 
    "AUDUSD=X": "AUD/USD",
    "EURUSD=X": "EUR/USD"
}

def get_market_info():
    # Фікс часу: додаємо 3 години до UTC для Києва
    kyiv_time = datetime.utcnow() + timedelta(hours=3)
    summary = f"⏰ ЧАС (Київ): {kyiv_time.strftime('%Y-%m-%d %H:%M')}\n"
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
    print("🚀 Паравоз виїхав! Час та точність ліміток налаштовано.")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            # Оновлений промпт для точних точок входу (ICT/Smart Money)
            prompt = f"""
            Ти професійний ICT трейдер. Твій стиль — робота в зонах OTE (0.62-0.79) та ретест FVG.
            
            Дані ринку: 
            {market_data}
            
            Твоє завдання:
            1. Проаналізуй DXY. Якщо він падає — шукай лонги по FX/Gold.
            2. Для кожного активу визнач POI (зону інтересу).
            3. ВАЖЛИВО: Не став лімітки занадто далеко. Шукай вхід на найближчому FVG або рівні 0.5 (Equilibrium) поточного ранкового імпульсу.
            4. Видай конкретну лімітку (Entry, SL, TP).

            Пиши українською з емодзі. Формат:
            📊 КОНТЕКСТ РИНКУ
            🎯 АКТУАЛЬНІ ЛІМІТКИ (максимально точні точки входу)
            🚀 ЛОГІКА (чому саме ця зона OTE або FVG)
            """
            
            response = model.generate_content(prompt)
            
            # Додаємо перевірку на Markdown, щоб не було помилок як у логах
            try:
                bot.send_message(CHANNEL_ID, response.text, parse_mode="Markdown")
            except:
                bot.send_message(CHANNEL_ID, response.text)
                
            kyiv_now = datetime.utcnow() + timedelta(hours=3)
            print(f"✅ СИГНАЛ ВІДПРАВЛЕНО: {kyiv_now.strftime('%H:%M')}")
            
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
