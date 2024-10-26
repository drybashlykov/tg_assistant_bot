import json
from telebot import TeleBot
from telebot import types
from time import sleep

def med_reminder():
    # CONFIG
    with open('config.json') as f:
        config = json.load(f)

    API_TOKEN = config["tg_API_token"]
    target_chat_id = config["med_reminder"]["target_chat_id"]
    med_reminder_text = config["med_reminder"]["med_reminder_text"]
    med_taken_label = config["med_reminder"]["med_taken_label"]

    bot = TeleBot(API_TOKEN)

    button_med_taken = types.InlineKeyboardButton(med_taken_label, callback_data='med_taken')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_med_taken)

    message = bot.send_message(target_chat_id, text=med_reminder_text, reply_markup=keyboard)
    
    return message.message_id

