import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# دیکشنری برای نگهداری وضعیت و حجم انتخابی کاربران
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


# منوی شروع و دکمه‌ی حجم دلخواه
@bot.message_handler(commands=['start'])
def send_welcome(message):
  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          '🎯 انتخاب حجم دلخواه (10 تا 500 گیگ)', callback_data='vol_custom'
      )
  )
  bot.send_message(
      message.chat.id,
      'سلام! به فروشگاه وی‌پی‌ان خوش آمدید.\nبرای خرید کانفیگ، لطفاً روی دکمه‌ی'
      ' زیر کلیک کنید:',
      reply_markup=markup,
  )


# مدیریت کلیک روی دکمه‌ی شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  if call.data == 'vol_custom':
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = {'step': 'waiting_for_custom_volume'}
    bot.send_message(
        call.message.chat.id,
        'لطفاً حجم دلخواه خود را به صورت عدد (بین **10** تا **500** گیگابایت)'
        ' در پیام بعدی ارسال کنید:',
    )


# دریافت و بررسی حجم دلخواه ارسالی از طرف کاربر (بازه ۱۰ تا ۵۰۰ گیگ)
@bot.message_handler(
    func=lambda message: user_states.get(message.chat.id, {}).get('step')
    == 'waiting_for_custom_volume'
)
def get_custom_volume(message):
  try:
    custom_vol = int(message.text)
    if 10 <= custom_vol <= 500:
      # ذخیره حجم و تغییر مرحله به انتظار برای ارسال رسید
      user_states[message.chat.id] = {
          'step': 'waiting_for_receipt',
          'volume': custom_vol,
      }
      bot.send_message(
          message.chat.id,
          f'شما حجم **{custom_vol} گیگابایت** را انتخاب کردید.\n\n'
          '💳 **اطلاعات پرداخت:**\n'
          'شماره کارت: `5859831128954681`\n'
          'به نام: **کسرا زارعی**\n\n'
          '📷 لطفاً پس از واریز وجه، **عکس رسید پرداخت** خود را همینجا ارسال'
          ' کنید.',
          parse_mode='Markdown',
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


# دریافت رسید پرداخت (عکس یا سند) از طرف کاربر
@bot.message_handler(
    content_types=['photo', 'document'],
    func=lambda message: user_states.get(message.chat.id, {}).get('step')
    == 'waiting_for_receipt',
)
def get_receipt(message):
  user_data = user_states.get(message.chat.id, {})
  volume = user_data.get('volume', 10)

  # پاک کردن وضعیت کاربر
  user_states[message.chat.id] = None

  bot.send_message(
      message.chat.id,
      '⏳ رسید شما برای مدیریت ارسال شد. به زودی پس از بررسی، کانفیگ برای شما'
      ' ارسال می‌گردد.',
  )

  # شبیه‌سازی تایید پرداخت و ارسال خودکار لینک کانفیگ (در نسخه‌های بعدی می‌توانید این را به پنل 3x-ui وصل کنید)
  bot.send_message(
      message.chat.id,
      '✅ پرداخت شما تأیید شد!\n\n🔑 **کانفیگ اختصاصی شما:**\n`vless://example-config-uuid-here@server-ip:443?encryption=none&security=tls&type=ws&path=%2F#KasraV2ray`',
      parse_mode='Markdown',
  )


if __name__ == '__main__':
  keep_alive()
  print('Bot is polling...')
  bot.infinity_polling()
  
