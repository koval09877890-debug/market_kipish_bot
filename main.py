import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime, timedelta

# 🔑 Налаштування (Railway Variables)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# Ініціалізація AI
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

bot = telebot.TeleBot(BOT_TOKEN)

# Список активів
SYMBOLS = {
    "DX-Y.NYB": "DXY (Індекс долара)", 
    "GC=F": "Gold (Золото)", 
    "GBPUSD=X": "GBP/USD", 
    "EURUSD=X": "EUR/USD",
    "AUDUSD=X": "AUD/USD (Озі)"
}

def get_market_info():
    # Розрахунок Київського часу (UTC+3)
    kyiv_time = datetime.utcnow() + timedelta(hours=3)
    summary = f"⏰ ЧАС: {kyiv_time.strftime('%d.%m %H:%M')} (Kyiv)\n\n"
    market_context = ""
    
    for ticker, name in SYMBOLS.items():
        try:
            data = yf.Ticker(ticker)
            # Беремо дані за останні 5 днів
            hist = data.history(period="5d")
            if hist.empty: continue
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            high_day = hist['High'].iloc[-1]
            low_day = hist['Low'].iloc[-1]
            change = ((current_price - prev_close) / prev_close) * 100
            
            fmt = ".2f" if any(x in name for x in ["Index", "Gold"]) else ".4f"
            
            summary += f"🔹 **{name}**: `{current_price:{fmt}}` ({change:+.2f}%)\n"
            market_context += (f"{name}: Зараз {current_price:{fmt}}, "
                              f"Денний High: {high_day:{fmt}}, Low: {low_day:{fmt}}. ")
        except Exception as e:
            print(f"Помилка даних для {ticker}: {e}")
            continue
            
    return summary, market_context

def run_kipish():
    print("🚀 Робот на Gemini 3 Flash (Forex) запущений...")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            stats_text, ai_context = get_market_info()
            
            # Жорсткіший промпт для аналізу ВСІХ пар
            prompt = f"""
            Ти — Senior Smart Money Трейдер (ICT стиль). 
            Твоя мета: дати сигнал для входу всередині дня, який ціна реально може зачепити найближчим часом.
            
            Дані ринку: 
            {ai_context}
            
            Твоє завдання:
            1. Зроби загальний короткий висновок по DXY.
            2. ОБОВ'ЯЗКОВО дай окремий сетап для КОЖНОЇ з трьох валютних пар: EUR/USD, GBP/USD та AUD/USD.
            3. Визнач Зони інтересу (POI) ТІЛЬКИ поблизу поточної ціни (не давай входи за 500 пунктів).
            
            Формат відповіді ДЛЯ КОЖНОЇ ПАРИ:
            📌 Актив: [Назва]
            Напрямок: [Bullish/Bearish]
            Точка входу: [Лімітка від FVG або OB]
            Take Profit: [найближча ліквідність]
            
            Пиши коротко, без зайвої води, професійним сленгом, українською мовою. 
            В кінці додай: "Не фінансова порада".
            """
            
            response = model.generate_content(prompt)
            full_message = f"{stats_text}\n📊 **АНАЛІЗ ТА ЛІМІТКИ (GEMINI)**\n\n{response.text}"
            
            bot.send_message(CHANNEL_ID, full_message, parse_mode="Markdown")
            
            kyiv_time = datetime.utcnow() + timedelta(hours=3)
            print(f"✅ Сигнал відправлено о {kyiv_time.strftime('%H:%M')}")
            
            # Пауза 1 година (3600 секунд)
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
