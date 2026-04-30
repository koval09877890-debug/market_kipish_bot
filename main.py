import telebot
import os
import google.generativeai as genai
import yfinance as yf
import time
from datetime import datetime, timedelta

# 🔑 Налаштування з твого Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')
bot = telebot.TeleBot(BOT_TOKEN)

# Твій словник пар
SYMBOLS = {
    "фунт": "GBPUSD=X",
    "золото": "GC=F",
    "євро": "EURUSD=X",
    "австралієць": "AUDUSD=X"
}

def get_rsi(ticker_symbol):
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
    bot.send_message(message.chat.id, "Привіт, Апурва! Напиши назву пари (фунт, золото, євро), і я зроблю розбір.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.lower()
    found_ticker = None
    
    for key, ticker in SYMBOLS.items():
        if key in text:
            found_ticker = ticker
            pair_name = key.upper()
            break

    if found_ticker:
        bot.send_message(message.chat.id, f"🚀 Обробляю {pair_name}...")
        
        try:
            # Збір ринкових цифр
            price = yf.Ticker(found_ticker).fast_info['last_price']
            rsi_val = get_rsi(found_ticker)
            dxy = yf.Ticker("DX-Y.NYB").fast_info['last_price']
            kyiv_time = (datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')

            prompt = f"Пара {pair_name}, Ціна {price}, RSI {rsi_val}, DXY {dxy:.2f}. Ти Smart Money трейдер. Дай прогноз: макро (Polymarket), де знімемо стопи (Stop Hunt) і точну лімітку (Entry/SL/TP). Пиши українською."
            
            response = model.generate_content(prompt)
            full_msg = f"💎 **{pair_name}** | {kyiv_time}\n\n{response.text}"
            
            bot.send_message(CHANNEL_ID, full_msg, parse_mode="Markdown")
            bot.send_message(message.chat.id, "✅ Готово! Дивись у каналі.")
        except Exception as e:
            bot.send_message(message.chat.id, "⚠️ Щось пішло не так при запиті даних.")
    else:
        bot.send_message(message.chat.id, "Напиши: фунт, золото або євро.")

if __name__ == "__main__":
    print("🤖 Бот активний...")
    bot.infinity_polling()
