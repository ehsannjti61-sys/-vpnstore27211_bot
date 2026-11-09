import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "9239059091:AAGcs7xr3ygvyBqHWQz1RNthA50acyG3zhA"
bot = telebot.TeleBot(TOKEN)

# ---------------------------------------------------------
# تنظیمات ادمین، کانال عضویت اجباری و کانفیگ دستی:
ADMIN_ID = 7855258378
CHANNEL_USERNAME = "@hfjrbdjd"  # کانال عضویت اجباری
MY_CUSTOM_CONFIG = "vless://your-real-config-uuid-here@your-server-ip:443?encryption=none&security=tls&type=ws&path=%2F#VPN-Store"
# ---------------------------------------------------------

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


# تابع بررسی عضویت کاربر در کانال
def check_membership(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if member.status in ['member', 'administrator', 'creator']:
      return True
  except Exception as e:
    print(f"Error checking membership: {e}")
  return False


# منوی شروع و بررسی عضویت اجباری
@bot.message_handler(commands=['start'])
def send_welcome(message):
  user_id = message.from_user.id

  # بررسی عضویت اجباری
  if not check_membership(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            '🔗 عضویت در کانال', url=f'https://t.me/hfjrbdjd'
        )
    )
    markup.add(
        InlineKeyboardButton(
            '✅ عضو شدم، بررسی مجدد', callback_data='check_join'
        )
    )
    bot.send_message(
        message.chat.id,
        '❌ برای استفاده از ربات و خرید کانفیگ، ابتدا باید در کانال ما عضو'
        f' شوید:\n{CHANNEL_USERNAME}\n\nپس از عضویت، روی دکمه‌ی «عضو شدم» کلیک'
        ' کنید.',
        reply_markup=markup,
    )
    return

  # اگر عضو بود، منوی اصلی خرید
  show_main_menu(message.chat.id)


def show_main_menu(chat_id):
  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          '🎯 انتخاب حجم دلخواه (10 تا 500 گیگ)', callback_data='vol_custom'
      )
  )
  bot.send_message(
      chat_id,
      'سلام! به فروشگاه وی‌پی‌ان خوش آمدید.\nبرای خرید کانفیگ، لطفاً روی دکمه‌ی'
      ' زیر کلیک کنید:',
      reply_markup=markup,
  )


# مدیریت کلیک روی دکمه‌های شیشه‌ای
@bot.callback_query_handler(
    func=lambda call: call.data.startswith('vol_')
    or call.data.startswith('admin_')
    or call.data == 'check_join'
)
def callback_query(call):
  user_id = call.from_user.id

  # بررسی دکمه عضو شدم
  if call.data == 'check_join':
    if check_membership(user_id):
      bot.answer_callback_query(call.id, 'عضویت شما تایید شد! 🎉')
      try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
      except:
        pass
      show_main_menu(call.message.chat.id)
    else:
      bot.answer_callback_query(
          call.id, 'شما هنوز در کانال عضو نشده‌اید!', show_alert=True
      )
    return

  # بررسی عضویت برای سایر دکمه‌ها
  if not check_membership(user_id):
    bot.answer_callback_query(
        call.id, 'ابتدا باید در کانال عضو شوید!', show_alert=True
    )
    return

  if call.data == 'vol_custom':
    bot.answer_callback_query(call.id)
    user_states[call.message.chat.id] = {'step': 'waiting_for_custom_volume'}
    bot.send_message(
        call.message.chat.id,
        'لطفاً حجم دلخواه خود را به صورت عدد (بین **10** تا **500** گیگابایت)'
        ' در پیام بعدی ارسال کنید:',
    )

  # تایید رسید توسط ادمین
  elif call.data.startswith('admin_approve_'):
    target_user_id = int(call.data.split('_')[2])
    bot.answer_callback_query(call.id, 'رسید تایید شد و کانفیگ ارسال گردید.')
    bot.send_message(
        target_user_id,
        '✅ پرداخت شما توسط مدیریت تأیید شد!\n\n🔑 **کانفیگ اختصاصی شما:**\n`'
        + MY_CUSTOM_CONFIG
        + '`',
        parse_mode='Markdown',
    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=(
            call.message.caption or ''
        )
        + '\n\n🟢 **وضعیت: تایید شده و کانفیگ ارسال شد.**',
        reply_markup=None,
    )

  # رد رسید توسط ادمین
  elif call.data.startswith('admin_reject_'):
    target_user_id = int(call.data.split('_')[2])
    bot.answer_callback_query(call.id, 'رسید رد شد.')
    bot.send_message(
        target_user_id,
        '❌ رسید پرداخت شما توسط مدیریت رد شد یا نامعتبر بود. لطفاً دوباره'
        ' بررسی کنید یا با پشتیبانی در ارتباط باشید.',
    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=(
            call.message.caption or ''
        )
        + '\n\n🔴 **وضعیت: رد شده.**',
        reply_markup=None,
    )


# دریافت و بررسی حجم دلخواه ارسالی از طرف کاربر
@bot.message_handler(
    func=lambda message: user_states.get(message.chat.id, {}).get('step')
    == 'waiting_for_custom_volume'
)
def get_custom_volume(message):
  if not check_membership(message.from_user.id):
    bot.send_message(
        message.chat.id,
        f'❌ ابتدا باید در کانال {CHANNEL_USERNAME} عضو شوید.',
    )
    return

  try:
    custom_vol = int(message.text)
    if 10 <= custom_vol <= 500:
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


# دریافت رسید پرداخت (عکس یا سند) از طرف کاربر و ارسال برای ادمین
@bot.message_handler(
    content_types=['photo', 'document'],
    func=lambda message: user_states.get(message.chat.id, {}).get('step')
    == 'waiting_for_receipt',
)
def get_receipt(message):
  if not check_membership(message.from_user.id):
    return

  user_data = user_states.get(message.chat.id, {})
  volume = user_data.get('volume', 10)
  user_states[message.chat.id] = None

  bot.send_message(
      message.chat.id,
      '⏳ رسید شما برای مدیریت ارسال شد. پس از بررسی و تایید، کانفیگ برای شما'
      ' ارسال می‌گردد.',
  )

  # ساخت دکمه‌های تایید و رد برای ادمین
  markup = InlineKeyboardMarkup()
  markup.row_width = 2
  markup.add(
      InlineKeyboardButton(
          '✅ تایید و ارسال کانفیگ',
          callback_data=f'admin_approve_{message.chat.id}',
      ),
      InlineKeyboardButton('❌ رد رسید', callback_data=f'admin_reject_{message.chat.id}'),
  )

  caption_text = (
      f'📥 **رسید جدید دریافت شد!**\n\n'
      f'👤 کاربر: @{message.from_user.username or "ندارد"} (ID:'
      f' `{message.chat.id}`)\n'
      f'📦 حجم درخواستی: **{volume} گیگابایت**'
  )

  if message.photo:
    file_id = message.photo[-1].file_id
    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=caption_text,
        reply_markup=markup,
        parse_mode='Markdown',
    )
  elif message.document:
    file_id = message.document.file_id
    bot.send_document(
        ADMIN_ID,
        file_id,
        caption=caption_text,
        reply_markup=markup,
        parse_mode='Markdown',
    )


if __name__ == '__main__':
  keep_alive()
  print('Bot is polling...')
  bot.infinity_polling()
  
