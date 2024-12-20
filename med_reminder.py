import json
from telebot import TeleBot
from telebot import types
from time import sleep
import threading


class MedState:
    def __init__(self):
        self.message_id = "0"

        # -1 for not yet started, 
        # 1 for keep reminding, 
        # 0 for stop reminding
        self.keep_reminding = -1
        
def update_state(state):
    state.keep_reminding = 0


def med_reminder(config):

    # CONFIG

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


def med_repeater(config, state):
    state.message_id = med_reminder(config)
    state.keep_reminding = 1
    reminder_counter = 1
    interval = 5

    if config["med_reminder"]["mode"] == "normal":
        multiplier = 60
    elif config["med_reminder"]["mode"] == "testing":
        multiplier = 1
    while state.keep_reminding:
        if reminder_counter > 3:
            interval = 60
        sleep(interval * multiplier)
        if state.keep_reminding:
            state.message_id = med_reminder(config)
            reminder_counter += 1


def start_med_repeater(config, linked_objects):
    state = MedState()
    linked_objects.med_reminder_state = state
    th = threading.Thread(target=med_repeater, args=[config, state])
    th.daemon = True
    th.start()