import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
import pandas as pd
from datetime import datetime, timedelta

# 🔑 Конфігурація
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')
bot = telebot.TeleBot(BOT_TOKEN)

# Твої робочі інструменти
SYMBOLS = {
    "GBPUSD=X": "GBP/USD", 
    "GC=F": "GOLD (XAU/USD)", 
    "EURUSD=X": "EUR/USD",
    "AUDUSD=X": "AUD/USD",
    "DX-Y.NYB": "DXY (Dollar Index)"
}

def calculate_rsi(ticker_symbol):
    try:
        data = yf.download(ticker_symbol, period="1d", interval="15m", progress=False)
        if data.empty: return "N/A"
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (100 + rs))
        return f"{rsi.iloc[-1]:.2f}"
    except: return "N/A"

def run_kipish():
    print("🚀 Запускаємо поштучний аналіз пар...")
    while True:
        try:
            kyiv_time = (datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')
            
            for ticker, name in SYMBOLS.items():
                price = yf.Ticker(ticker).fast_info['last_price']
                rsi_val = calculate_rsi(ticker)
                fmt = ".4f" if "USD" in name else ".2f"
                
                # Короткий, але потужний промпт для кожної пари
                prompt = f"""
                Пара: {name}
                Ціна зараз: {price:{fmt}}
                RSI (15m): {rsi_val}
                Час: {kyiv_time}
                
                Ти професійний трейдер Smart Money. Дай короткий аналіз (до 500 символів):
                1. Полімаркет/Макро: як новини впливають на {name}?
                2. Stop Hunt: Де стоять стопи натовпу (BSL/SSL)?
                3. Лімітка: Точна точка входу, SL та TP.
                4. Висновок: Купуємо винос чи чекаємо ретест?
                
                Пиши українською, лаконічно, з емодзі.
                """
                
                response = model.generate_content(prompt)
                
                msg = f"💎 **{name}** | {kyiv_time}\n\n{response.text}"
                
                try:
                    bot.send_message(CHANNEL_ID, msg, parse_mode="Markdown")
                except:
                    bot.send_message(CHANNEL_ID, msg)
                
                time.sleep(5) # Пауза між повідомленнями, щоб Telegram не забанив
            
            print(f"✅ Всі пари оновлено о {kyiv_time}. Чекаємо годину.")
            time.sleep(3600)
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_kipish()
