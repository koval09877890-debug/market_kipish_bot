import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime

# 🔑 Дані з Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

# Розширений список символів
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
    print("🚀 Паравоз виїхав з новими агресивними лімітками!")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            # ОНОВЛЕНИЙ ПРОМПТ ДЛЯ ТОЧНІШИХ ВХОДІВ (ICT Style)
            prompt = f"""
            Ти професійний Smart Money трейдер (стиль ICT). 
            Твій пріоритет — висока точність та входи, які не треба чекати вічність.
            
            Дані ринку: 
            {market_data}
            
            Твоє завдання:
            1. Проаналізуй структуру MS (Market Structure) та силу DXY.
            2. Знайди найближчий FVG (Fair Value Gap) або локальний Order Block.
            3. ВАЖЛИВО: Не став лімітки занадто далеко від ціни. Якщо тренд сильний, використовуй рівень 0.5 (Equilibrium) або зону OTE (0.62-0.79) поточного імпульсу.
            4. Врахуй макроекономіку та Polymarket (ставки, інфляція).
            
            Формат відповіді (УКРАЇНСЬКОЮ):
            📊 **КОНТЕКСТ РИНКУ** (Коротко: DXY та загальний настрій)
            🎯 **АКТУАЛЬНІ ЛІМІТКИ** (Buy/Sell Limit, Entry, SL, TP — максимально наближені до поточних значень)
            🚀 **ЛОГІКА ВХОДУ** (Поясни: ретест FVG, зняття ліквідності чи OTE)
            """
            
            response = model.generate_content(prompt)
            
            bot.send_message(CHANNEL_ID, response.text, parse_mode="Markdown")
            print(f"✅ СИГНАЛ ВІДПРАВЛЕНО: {datetime.now().strftime('%H:%M')}")
            
            # Чекаємо 1 годину (3600 сек)
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
