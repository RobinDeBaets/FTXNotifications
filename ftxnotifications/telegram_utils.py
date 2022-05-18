import os

import telebot
from dotenv import load_dotenv
from retry import retry

load_dotenv()

TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

tb = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="Markdown")


@retry(tries=30, delay=10)
def send_telegram(message):
    """
    Sends notification to telegram
    """
    tb.send_message(TELEGRAM_CHAT, message)
