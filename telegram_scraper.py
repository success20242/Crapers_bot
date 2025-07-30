from telethon.sync import TelegramClient
import re

api_id = 21993597
api_hash = '3648f9e2efb3e88365a954ecbbf987c5'
channels = ['@BettingTipsVIP', '@FixedMatchesHQ', '@SureOddsDaily']  # you can add more

client = TelegramClient('session_name', api_id, api_hash)

def extract_predictions(text):
    return re.findall(r'.*?vs.*?(?:Over|Under|Win|Draw|BTTS).*', text, re.IGNORECASE)

def get_telegram_predictions():
    predictions = []
    with client:
        for channel in channels:
            for message in client.iter_messages(channel, limit=30):
                if message.text:
                    picks = extract_predictions(message.text)
                    predictions.extend(picks)
    return predictions
