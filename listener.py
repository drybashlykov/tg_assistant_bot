# IMPORTS

import asyncio
import json
import threading
import os
from time import sleep
from med_reminder import med_reminder
from horoscope import horoscope

from telebot import TeleBot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# DEFINE VARIABLES

class State:
    def __init__(self):
        self.message_id = "0"

        # -1 for not yet started, 
        # 1 for keep reminding, 
        # 0 for stop reminding
        self.keep_reminding = -1

# DEFINE SCHEDULER

def setup_scheduler():
    scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 15*60},)
    scheduler.start()

    med_trigger = CronTrigger(
        year="*", month="*", day="*", hour="9", minute="50", second="0"
    )

    horoscope_trigger = CronTrigger(
        year="*", month="*", day="*", hour="7", minute="30", second="0"
    )

    scheduler.add_job(  
        start_med_repeater,
        trigger=med_trigger,
        args=[],
        name="med reminder",
    )

    scheduler.add_job(  
        horoscope,
        trigger=horoscope_trigger,
        args=[],
        name="horoscope",
    )

# DEFINE MED_REPEATER

def med_repeater():
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
    th = threading.Thread(target=med_repeater)
    th.daemon = True
    th.start()

# START SCHEDULER

setup_scheduler()

# LOAD CONFIG

with open('config.json') as f:
    config = json.load(f)

# CREATE STATE VARIABLES

state = State()  # Create a shared state object

API_TOKEN = config["tg_API_token"]
med_taken_response = config["med_reminder"]["med_taken_response"]
target_chat_id_M = config["med_reminder"]["target_chat_id"]
med_taken_edit_message = config["med_reminder"]["med_taken_edit_message"]

# Initialize the bot with your token
bot = TeleBot(API_TOKEN)
# report_handler = socketserver.TCPServer((HOST, PORT), TCPReportHandler)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, f"Echo: {message.text}")

# For med_reminder
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "med_taken":
        bot.answer_callback_query(call.id, med_taken_response)
        bot.edit_message_text(med_taken_edit_message, target_chat_id_M, state.message_id, reply_markup=None)
        state.keep_reminding = 0

bot.infinity_polling()