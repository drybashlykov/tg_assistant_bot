import json
from telebot import TeleBot
from telebot import types
from time import sleep
import threading
from datetime import datetime

        
def update_state(state):
    state.keep_reminding = 0

def log_reply(config, message):
    with open("weight_log.txt", "a") as f:
        prefix = config["weight_tracker"]["reminder_prefix"]
        date = message.reply_to_message.text[len(prefix):]
        weight = message.text
        f.write(date + "\t" + str(weight) + "\n")

def weight_tracker(config, linked_objects):

    # CONFIG

    API_TOKEN = config["tg_API_token"]
    target_chat_id = config["weight_tracker"]["target_chat_id"]

    bot = TeleBot(API_TOKEN)

    # button_weight_taken = types.InlineKeyboardButton(weight_taken_label, callback_data='weight_taken')

    # keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(button_weight_taken)
    today = datetime.today().strftime("%Y-%m-%d")

    message = bot.send_message(target_chat_id, text= 
                               config["weight_tracker"]["reminder_prefix"] + today)
    
    return message.message_id