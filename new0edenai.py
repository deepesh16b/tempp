import asyncio
import yfinance as yf
from datetime import datetime, timedelta
from telethon.sync import TelegramClient
import telebot
import pytz
import requests
import json
all_news = ''
BOT_API_KEY = '6665531132:AAGLcj_90SKyWOIYASuBsuKgdVzl0sHQe_Q'
OPENAI_API_KEY = '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'
api_id = 10173687
api_hash ='727a2cb034b172dce74d3a7f0ee14e4a'

# Define the ticker symbol
ticker_symbol = "TCS.NS"
# Define Telegram chats
chats = ['STOCK_MARKET_NEWS_UPDATE']

# Initialize Telegram client
client = TelegramClient('stockPick', api_id, api_hash)

# Initialize Telebot
bot = telebot.TeleBot(BOT_API_KEY)

async def find_news():
    # Define the date range
    end_date = datetime.now(tz=pytz.timezone('Asia/Kolkata')) + timedelta(days=1)  # Today's date plus 1 day in IST
    start_date = end_date - timedelta(days=5)      # 5 days before the end date
    # Get the last date of the market open
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
    last_market_open_date = stock_data.index[-1].strftime('%Y-%m-%d')

    # Initialize an empty list to store messages
    messages = []

    # Define start date for fetching Telegram messages
    start_date_telegram = datetime.strptime(last_market_open_date + ' 13:40', '%Y-%m-%d %H:%M')

    # Iterate over chats and fetch messages
    async with client:
        for chat in chats:
            async for message in client.iter_messages(chat, offset_date=start_date_telegram, reverse=True):
                messages.append(f'News: {message.text}')

    # Join all message texts into a single string
    combined_news = '\n'.join(messages)
    # print(combined_news)
    return combined_news

def ChatModal(prompt):

    url = "https://api.edenai.run/v2/text/chat"

    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "temperature": 0,
        "max_tokens": 1000,
        "providers": "google",
        "text": prompt,
        "chatbot_global_action": "stocks market india"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjExNTk5MzgtM2I4Zi00ZTZmLWJhYzYtYTEyN2U3YzZjYzg4IiwidHlwZSI6ImFwaV90b2tlbiJ9.p3fjagruMHJvC68AUtcUSm-zh42rywxPPJqI2Gc3Wlw"
    }

    response = requests.post(url, json=payload, headers=headers)

    # print(response.text)
    data = json.loads(response.text)
    return data['google']['generated_text']

@bot.message_handler(['start'])
def start(message):
    bot.reply_to(message, "Hello!\nWelcome to Today's Top Stocks Bot.\nSend '/find' for a today's top stocks list.")

@bot.message_handler(['find'])
def find(message):
    global all_news
    query = 'I am giving you some share market news of past few hours, you just have to tell me top 5 stocks that are likely to show positive affect tomorrow and top 5 stocks that are likely to show negative affect on tomorrow you can analyse it by like how big they have win an order.just give me their names.'
    query = str(query) + str(all_news)
    resulted_ai_stocks = ChatModal(query)
    bot.reply_to(message, resulted_ai_stocks)

async def main() -> None:
    print('Bot is Running...')
    global all_news
    all_news = await find_news()
    bot.polling(timeout=400)

if __name__ == "__main__":
    asyncio.run(main())
