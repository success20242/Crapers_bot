from telethon.sync import TelegramClient
import json
import re

with open('config.json') as f:
    config = json.load(f)

api_id = 21993597
api_hash = '3648f9e2efb3e88365a954ecbbf987c5'

client = TelegramClient('session_name', api_id, api_hash)

def fetch_telegram_predictions(limit=10):
    predictions = []
    client.start()

    for url in config['telegram_channels']:
        channel = url.split("/")[-1]
        for message in client.iter_messages(channel, limit=limit):
            if message.text:
                text = message.text
                if "vs" in text.lower() or "correct score" in text.lower():
                    predictions.append(text)

    client.disconnect()
    return predictions
