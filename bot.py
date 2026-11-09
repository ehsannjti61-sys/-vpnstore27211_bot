import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# دیکشنری موقت برای ذخیره وضعیت کاربران
user_states = {}

# سرور وب برای پاسخ به رندر و روشن نگه داشتن ربات
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
      InlineKeyboardButton(
          'حجم دلخواه (10 تا 500 گیگ)', callback_data='vol_custom'
      ),
      InlineKeyboardButton('حجم نامحدود', callback_data='vol_unlimited'),
  )
  bot.send_message(
      message.chat.id,
      'سلام! به فروشگاه وی‌پی‌ان خوش آمدید. \nلطفاً حجم کانفیگ مورد نظر خود را'
      ' انتخاب کنید:',
      reply_markup=markup,
  )


# مدیریت کلیک روی دکمه‌های شیشه‌ای
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
  elif call.data == 'vol_custom':
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = 'waiting_for_custom_volume'
    bot.send_message(
        call.message.chat.id,
        'لطفاً حجم دلخواه خود را به صورت عدد (بین **10** تا **500** گیگابایت)'
        ' در پیام بعدی ارسال کنید:',
    )


# دریافت و بررسی حجم دلخواه ارسالی از طرف کاربر (بازه ۱۰ تا ۵۰۰ گیگ)
@bot.message_handler(
    func=lambda message: user_states.get(message.chat.id)
    == 'waiting_for_custom_volume'
)
def get_custom_volume(message):
  try:
    custom_vol = int(message.text)
    if 10 <= custom_vol <= 500:
      # پاک کردن وضعیت کاربر پس از دریافت مقدار معتبر
      user_states[message.chat.id] = None
      bot.send_message(
          message.chat.id,
          f'شما حجم **{custom_vol} گیگابایت** را به صورت دلخواه انتخاب'
          ' کردید.\nبرای نهایی شدن خرید، لطفاً وجه را پرداخت کرده و رسید آن را'
          ' ارسال کنید.',
      )
    else:
      bot.send_message(
          message.chat.id,
          '❌ حجم وارد شده باید عددی بین **10** تا **500** باشد. لطفاً دوباره'
          ' عدد معتبری ارسال کنید:',
      )
  except ValueError:
    bot.send_message(
        message.chat.id,
        '❌ لطفاً فقط یک **عدد صحیح** (مثلاً 50) بین 10 تا 500 ارسال کنید:',
    )


if __name__ == '__main__':
  keep_alive()
  print('Bot is polling...')
  bot.infinity_polling()
  
