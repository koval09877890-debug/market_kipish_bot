import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime

# 🔑 Дані з Railway (залишаємо як було)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

# Розширений список символів (DXY обов'язково!)
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
    print("🚀 Паравоз виїхав з лімітками!")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            # ОНОВЛЕНИЙ ПРОМПТ З ЛІМІТКАМИ
            prompt = f"""
            Ти професійний Smart Money трейдер. Твій стиль — пошук ліквідності (BSL/SSL) та робота від OB (Order Block).
            
            Дані: 
            {market_data}
            
            Твоє завдання:
            1. Проаналізуй DXY (силу долара).
            2. Для золота та валютних пар визнач ймовірні Зони інтересу (POI).
            3. Напиши конкретні рівні для лімітних ордерів (Buy Limit / Sell Limit) та цілі (TP).
            4. Врахуй макроекономіку та Polymarket (ставки, інфляція).
            
            Напиши аналіз українською мовою з емодзі. Структура:
            📊 Контекст ринку
            🎯 Лімітки (точки входу)
            🚀 Цілі (ліквідність)
            """
            
            response = model.generate_content(prompt)
            
            bot.send_message(CHANNEL_ID, response.text)
            print(f"✅ СИГНАЛ ВІДПРАВЛЕНО: {datetime.now().strftime('%H:%M')}")
            
            # Чекаємо 1 годину (3600 сек)
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
