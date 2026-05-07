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

# Ініціалізація AI (Використовуємо Gemini 3 Flash)
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
    summary = f"⏰ ЧАС: {datetime.now().strftime('%d.%m %H:%M')} (Kyiv)\n\n"
    market_context = ""
    
    for ticker, name in SYMBOLS.items():
        try:
            data = yf.Ticker(ticker)
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
    print("🚀 Робот на Gemini 3 (Forex + AUD/USD) у роботі...")
    while True:
        try:
            if not CHANNEL_ID:
                print("❌ CHANNEL_ID не знайдено!")
                time.sleep(60)
                continue
                
            stats_text, ai_context = get_market_info()
            
            # ОНОВЛЕНО: Тепер Gemini аналізує КОЖЕН актив окремо
            prompt = f"""
            Ти — Senior Smart Money Трейдер (ICT стиль). 
            Твоє завдання: провести аналіз для КОЖНОГО активу зі списку окремо.
            
            Дані ринку: 
            {ai_context}
            
            ПЛАН РОБОТИ:
            1. Проаналізуй силу DXY та його вплив на інші пари.
            2. Для КОЖНОГО активу (Gold, GBP/USD, EUR/USD, AUD/USD) визнач:
               - Bias (Напрямок: Bullish/Bearish).
               - POI (Точка входу): шукай найближчі зони (OB, FVG) на M15/H1. Вхід має бути реальним (15-40 пунктів від ціни).
               - Take Profit (найближчий рівень ліквідності).
            
            Якщо по якомусь активу немає чіткого сигналу — пиши "Поза ринком / Очікування".
            Пиши коротко, професійною мовою ICT, українською, з емодзі.
            В кінці додай: "Не фінансова порада".
            """
            
            response = model.generate_content(prompt)
            full_message = f"{stats_text}\n📊 **АНАЛІЗ ТА ЛІМІТКИ (GEMINI 3)**\n\n{response.text}"
            
            bot.send_message(CHANNEL_ID, full_message, parse_mode="Markdown")
            print(f"✅ Сигнали по всіх парах відправлено: {datetime.now().strftime('%H:%M')}")
            
            # Пауза 2 години для уникнення лімітів API
            time.sleep(7200)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
