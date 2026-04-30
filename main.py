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

# Список символів
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
    print("🚀 Паравоз виїхав! Режим: Розумні входи та виправлений час.")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            # Оновлений промпт: жорстке порівняння цін
            prompt = f"""
            Ти професійний ICT трейдер. Твій стиль — робота в зонах OTE (0.62-0.79) та ретест FVG.
            
            Ось реальні ціни зараз: 
            {market_data}
            
            Твоє завдання:
            1. Проаналізуй структуру ринку.
            2. Порівняй ціну лімітки з актуальними даними з ринку вище. 
            3. ВАЖЛИВО: Якщо ти хочеш дати Buy Limit — ціна Entry МАЄ бути НИЖЧОЮ за поточну. 
            4. Якщо ціна вже стоїть на твоєму рівні або дуже близько — не пиши "Limit", пиши "ВХІД ПО РИНКУ (MARKET)".
            5. Не давай застарілих рівнів, які ціна вже пролетіла.

            Пиши українською з емодзі. Формат:
            📊 **КОНТЕКСТ РИНКУ**
            🎯 **АКТУАЛЬНІ ВХОДИ** (Market або Limit з чіткими цифрами)
            🚀 **ЛОГІКА** (чому саме ця зона)
            """
            
            response = model.generate_content(prompt)
            
            # Відправка з обробкою помилок розмітки
            try:
                bot.send_message(CHANNEL_ID, response.text, parse_mode="Markdown")
            except:
                bot.send_message(CHANNEL_ID, response.text)
                
            kyiv_now = datetime.utcnow() + timedelta(hours=3)
            print(f"✅ СИГНАЛ ВІДПРАВЛЕНО: {kyiv_now.strftime('%H:%M')}")
            
            # Чекаємо 1 годину (3600 сек)
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
