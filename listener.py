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

# DEFINE SCHEDULER

def setup_scheduler():
    scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 15*60})

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

# START SCHEDULER

setup_scheduler()

# LOAD CONFIG

config_path = sys.argv[1]
with open(config_path) as f:
    config = json.load(f)

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