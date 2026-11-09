import os
from threading import Thread
from flask import Flask
import telebot  # یا هر کتابخونه‌ای که استفاده می‌کنی

# تنظیمات ربات
TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# یک سرور وب ساده برای اینکه رندر فکر کنه وب‌سایت است و ارور پورت نده
app = Flask('')


@app.route('/')
def home():
  return "Bot is running online!"


def run_web():
  # رندر به طور خودکار پورت رو از متغیر محیطی پورت می‌خونه
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


# اجرای سرور وب در پس‌زمینه
def keep_alive():
  t = Thread(target=run_web)
  t.start()


# دستورات ربات (نمونه)
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "سلام! ربات وی‌پی‌ان فروشگاه روشن شد.")


if __name__ == '__main__':
  # اول وب‌سرور رو روشن می‌کنیم تا رندر پورت رو باز ببینه
  keep_alive()
  # بعد ربات تلگرام رو استارت می‌کنیم
  print("Bot is polling...")
  bot.infinity_polling()
  
