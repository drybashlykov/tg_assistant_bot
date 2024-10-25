# This should always be running.

import asyncio
from telebot import TeleBot

with open("config") as f:
    token_line = f.readline()

print("This should be the token: ", token_line[15:])

# Initialize the bot with your token
API_TOKEN = token_line[15:] 
bot = TeleBot(API_TOKEN)

@bot.message_handler(func=lambda msg: True)
async def echo_all(message):
    await bot.reply_to(message, f"Echo: {message.text}")

# Main function to run both polling and scheduled tasks
bot.infinity_polling()

