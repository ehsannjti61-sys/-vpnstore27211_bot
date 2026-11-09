import os
from threading import Thread
from flask import Flask
import telebot

# توکن ربات شما
TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# سرور وب کوچک برای پاسخ به رندر و جلوگیری از ارور
app = Flask('')


@app.route('/')
def home():
  return "Bot is running online!"


def run_web():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run_web)
  t.start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "سلام! فروشگاه وی‌پی‌ان با موفقیت آنلاین شد.")


if __name__ == '__main__':
  keep_alive()
  print("Bot is polling...")
  bot.infinity_polling()
  
