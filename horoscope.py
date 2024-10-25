import requests
import json
from telebot import TeleBot

def chatgpt_request(prompt, api_key):
    # Define the API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Create the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Define the request body with the model and messages
    data = {
        "model": "gpt-3.5-turbo",  # or "gpt-4" if you're using GPT-4
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,  # Adjust for creativity level (0 = deterministic, 1 = more creative)
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON and extract the assistant's reply
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    else:
        # Handle errors
        return f"Error: {response.status_code} - {response.text}"

# CONFIG
with open('config.json') as f:
    config = json.load(f)

API_TOKEN = config["tg_API_token"]
target_chat_id = config["horoscope_settings"]["target_chat_id"]
prompt = config["horoscope_settings"]["prompt"]
cute_gm_text = config["horoscope_settings"]["cute_gm_text"]

# response = chatgpt_request(prompt)

response = "Pretend it's a horoscope"

# Initialize the bot with your token
bot = TeleBot(API_TOKEN)

bot.send_message(chat_id=target_chat_id, text=cute_gm_text)
bot.send_message(chat_id=target_chat_id, text=response)
