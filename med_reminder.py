import json
from telebot import TeleBot
from telebot import types
from time import sleep
import threading


class State:
    def __init__(self):
        self.message_id = "0"

        # -1 for not yet started, 
        # 1 for keep reminding, 
        # 0 for stop reminding
        self.keep_reminding = -1


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


def med_repeater(state):
    state.message_id = med_reminder()
    state.keep_reminding = 1
    reminder_counter = 1
    interval = 5
    while state.keep_reminding:
        if reminder_counter > 3:
            interval = 60
        sleep(interval * 60)
        if state.keep_reminding:
            state.message_id = med_reminder()
            reminder_counter += 1


def start_med_repeater():
    state = State()

    th = threading.Thread(target=med_repeater, args=[state])
    th.daemon = True
    th.start()