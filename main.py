import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
import pandas as pd
from datetime import datetime, timedelta

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

def calculate_rsi(ticker_symbol, periods=14):
    try:
        data = yf.download(ticker_symbol, period="1d", interval="15m", progress=False)
        if data.empty: return "N/A"
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (100 + rs))
        return f"{rsi.iloc[-1]:.2f}"
    except:
        return "N/A"

def get_market_info():
    kyiv_now = datetime.utcnow() + timedelta(hours=3)
    summary = f"⏰ ЧАС (Київ): {kyiv_now.strftime('%Y-%m-%d %H:%M')}\n"
    summary += "📊 ТЕХНІЧНІ ДАНІ (RSI + Price):\n"
    for ticker, name in SYMBOLS.items():
        try:
            t = yf.Ticker(ticker)
            price = t.fast_info['last_price']
            rsi_val = calculate_rsi(ticker)
            fmt = ".2f" if "Index" in name or "Gold" in name else ".4f"
            summary += f"🔹 {name}: {price:{fmt}} (RSI: {rsi_val})\n"
        except:
            continue
    return summary

def run_kipish():
    print("🚀 Пошук грааля активовано! Полюємо на ліквідність.")
    while True:
        try:
            if not CHANNEL_ID:
                time.sleep(60)
                continue
                
            market_data = get_market_info()
            
            prompt = f"""
            Ти — професійний Smart Money та Institutional трейдер. Твоя спеціалізація: Stop Loss Hunting та Liquidity Sweeps.
            
            ДАНІ:
            {market_data}
            
            ЗАВДАННЯ:
            1. Проаналізуй макроекономічний фон та настрої на Polymarket (ставки FED, вибори, інфляція).
            2. Визнач зони BSL (Buy Side Liquidity) та SSL (Sell Side Liquidity), де натовп ставить стопи.
            3. Встанови лімітки (Buy/Sell Limit) саме за цими рівнями — там, де ринок забере ліквідність перед розворотом.
            4. Врахуй RSI: якщо RSI > 70 — шукай точку входу в шорт від OB, якщо < 30 — лонг від FVG.
            5. Поточна ціна має бути поруч! Не давай рівні, до яких ціна не дійде сьогодні.
            
            Структура (УКРАЇНСЬКОЮ):
            📊 КОНТЕКСТ ТА ЕКОНОМІКА
            🎯 ПОЛЮВАННЯ НА СТОПИ (Твої лімітки на зняття ліквідності)
            🛡 УПРАВЛІННЯ РИЗИКОМ (SL та TP)
            📈 RSI АНАЛІЗ (Чи перегрітий ринок?)
            """
            
            response = model.generate_content(prompt)
            
            try:
                bot.send_message(CHANNEL_ID, response.text, parse_mode="Markdown")
            except:
                bot.send_message(CHANNEL_ID, response.text)
                
            kyiv_log = datetime.utcnow() + timedelta(hours=3)
            print(f"✅ АНАЛІЗ ВІДПРАВЛЕНО: {kyiv_log.strftime('%H:%M')}")
            
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
