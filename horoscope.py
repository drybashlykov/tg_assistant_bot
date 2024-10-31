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


def horoscope(config, linked_objects):
    # CONFIG
    API_TOKEN = config["tg_API_token"]

    settings = config["horoscope_settings"]
    target_chat_id = settings["target_chat_id"]
    api_key = settings["chatgpt_api_key"]
    prompt = settings["prompt"]
    cute_gm_text = settings["cute_gm_text"]

    if settings["mode"] == "normal":
        response = chatgpt_request(prompt, api_key)
    elif settings["mode"] == "testing":
        response = "Pretend this is a horoscope"
    else:
        print("Invalid horoscope mode. Aborting.")

    # Initialize the bot with your token
    bot = TeleBot(API_TOKEN)

    bot.send_message(chat_id=target_chat_id, text=cute_gm_text)
    bot.send_message(chat_id=target_chat_id, text=response)

    return 0
