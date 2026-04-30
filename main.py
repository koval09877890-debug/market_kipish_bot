import telebot
import os
import google.generativeai as genai
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from telebot import types

# 🔑 Конфігурація
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')
bot = telebot.TeleBot(BOT_TOKEN)

# Налаштування пар
SYMBOLS = {
    "GBP/USD": "GBPUSD=X",
    "GOLD (XAU)": "GC=F",
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X"
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

def get_dxy_status():
    try:
        t = yf.Ticker("DX-Y.NYB")
        price = t.fast_info['last_price']
        return f"DXY: {price:.2f}"
    except: return "DXY: дані недоступні"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(s) for s in SYMBOLS.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Привіт, Апурва! Обери пару для миттєвого аналізу 📊", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in SYMBOLS.keys())
def handle_analysis(message):
    pair_name = message.text
    ticker = SYMBOLS[pair_name]
    
    bot.send_message(message.chat.id, f"🔍 Аналізую {pair_name}... Зачекай секунду.")
    
    # Збір даних
    price = yf.Ticker(ticker).fast_info['last_price']
    rsi_val = calculate_rsi(ticker)
    dxy = get_dxy_status()
    kyiv_time = (datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')
    
    prompt = f"""
    Інструмент: {pair_name}
    Ціна зараз: {price}
    RSI: {rsi_val}
    {dxy}
    Час: {kyiv_time}
    
    Ти — Smart Money Expert. Зроби повний розбір:
    1. Макро та Polymarket: що зараз впливає на актив?
    2. Stop Hunt: Де зони BSL/SSL, де ми заберемо ліквідність натовпу?
    3. Лімітка: Конкретний Buy/Sell Limit, Stop Loss та Take Profit.
    4. RSI порада: Чи не запізно входити?
    
    Пиши українською, чітко, для про-трейдера.
    """
    
    try:
        response = model.generate_content(prompt)
        full_msg = f"💎 **{pair_name}** | {kyiv_time}\n\n{response.text}"
        bot.send_message(message.chat.id, full_msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Сталася помилка при генерації аналізу.")

if __name__ == "__main__":
    print("🤖 Бот чекає на твої команди...")
    bot.infinity_polling()
