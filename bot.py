import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# سرور وب برای پاسخ به رندر
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


# منوی شروع و دکمه‌های شیشه‌ای انتخاب حجم کانفیگ
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = InlineKeyboardMarkup()
  markup.row_width = 2
  markup.add(
      InlineKeyboardButton('10 گیگابایت (1 ماهه)', callback_data='vol_10'),
      InlineKeyboardButton('20 گیگابایت (1 ماهه)', callback_data='vol_20'),
      InlineKeyboardButton('حجم دلخواه / نامحدود', callback_data='vol_unlimited'),
  )
  bot.send_message(
      message.chat.id,
      'سلام! به فروشگاه وی‌پی‌ان خوش آمدید. \nلطفاً حجم کانفیگ مورد نظر خود را'
      ' انتخاب کنید:',
      reply_markup=markup,
  )


# مدیریت کلیک روی دکمه‌ها
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  if call.data == 'vol_10':
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        'شما حجم **10 گیگابایت** را انتخاب کردید.\nبرای نهایی شدن خرید، لطفاً'
        ' وجه را پرداخت کرده و رسید آن را ارسال کنید.',
    )
  elif call.data == 'vol_20':
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        'شما حجم **20 گیگابایت** را انتخاب کردید.\nبرای نهایی شدن خرید، لطفاً'
        ' وجه را پرداخت کرده و رسید آن را ارسال کنید.',
    )
  elif call.data == 'vol_unlimited':
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        'شما حجم **نامحدود** را انتخاب کردید.\nبرای نهایی شدن خرید، لطفاً وجه'
        ' را پرداخت کرده و رسید آن را ارسال کنید.',
    )


if __name__ == '__main__':
  keep_alive()
  print('Bot is polling...')
  bot.infinity_polling()
  
