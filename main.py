import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# 🔑 Налаштування
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')
bot = telebot.TeleBot(BOT_TOKEN)

# Flask потрібен, щоб Railway не "вбивав" процес
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

SYMBOLS = {
    "фунт": "GBPUSD=X",
    "золото": "GC=F",
    "євро": "EURUSD=X",
    "австралієць": "AUDUSD=X"
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

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привіт! Напиши назву пари (наприклад: фунт, золото, євро), і я зроблю повний аналіз у канал.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.lower()
    found_ticker = None
    pair_name = ""

    for key, ticker in SYMBOLS.items():
        if key in text:
            found_ticker = ticker
            pair_name = key.upper()
            break

    if found_ticker:
        bot.reply_to(message, f"🚀 Готую аналіз для {pair_name}...")
        
        # Збір даних
        price = yf.Ticker(found_ticker).fast_info['last_price']
        rsi_val = calculate_rsi(found_ticker)
        dxy = yf.Ticker("DX-Y.NYB").fast_info['last_price']
        kyiv_time = (datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')

        prompt = f"""
        Ти — Smart Money Expert. Аналізуй {pair_name}.
        Ціна: {price}, RSI: {rsi_val}, DXY: {dxy:.2f}.
        Час: {kyiv_time}.
        
        Зроби прогноз: Полімаркет (ставки/макро), Stop Hunt (де знімемо ліквідність), конкретна лімітка Entry/SL/TP.
        Пиши українською з емодзі.
        """
        
        response = model.generate_content(prompt)
        full_msg = f"💎 **{pair_name} АНАЛІЗ** | {kyiv_time}\n\n{response.text}"
        
        # Відправка в канал
        bot.send_message(CHANNEL_ID, full_msg, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Готово! Перевір канал.")
    else:
        bot.reply_to(message, "Не впізнав пару. Спробуй: фунт, золото або євро.")

if __name__ == "__main__":
    # Запуск веб-сервера у фоні
    t = Thread(target=run_web)
    t.start()
    
    print("🤖 Бот запущений!")
    bot.infinity_polling()
