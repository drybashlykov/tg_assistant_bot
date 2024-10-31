# IMPORTS

import asyncio
import json
import threading
import os
from time import sleep
from med_reminder import start_med_repeater
from horoscope import horoscope
import sys

from telebot import TeleBot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from scheduler_setup_utils import setup_scheduler

config_path = sys.argv[1]
with open(config_path) as f:
    config = json.load(f)

# LINK INTERACTIVE MODULES

class LinkedObjects():
    def __init__(self):
        self.med_reminder_state = None

linked_objects = LinkedObjects()

# START SCHEDULER

scheduler = setup_scheduler(config, linked_objects)
scheduler.start()

# LOAD CONFIG

API_TOKEN = config["tg_API_token"]
med_taken_response = config["med_reminder"]["med_taken_response"]
target_chat_id_M = config["med_reminder"]["target_chat_id"]
med_taken_edit_message = config["med_reminder"]["med_taken_edit_message"]



# Initialize the bot with your token
bot = TeleBot(API_TOKEN)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, f"Echo: {message.text}")

# For med_reminder
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "med_taken":
        bot.answer_callback_query(call.id, med_taken_response)
        bot.edit_message_text(med_taken_edit_message,
                              target_chat_id_M,
                              linked_objects.med_reminder_state.message_id,
                              reply_markup=None)
        linked_objects.med_reminder_state.keep_reminding = 0

bot.infinity_polling()