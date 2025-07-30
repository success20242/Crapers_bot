from telethon.sync import TelegramClient
import re

# === Telegram API Credentials ===
api_id = 21993597
api_hash = '3648f9e2efb3e88365a954ecbbf987c5'

# === List of Channels to Scrape Predictions From ===
channels = [
    '@BettingTipsVIP',
    '@FixedMatchesHQ',
    '@SureOddsDaily',
    '@FreeDailyBettingTips'
]

# === Initialize Client ===
client = TelegramClient('session_name', api_id, api_hash)

# === Prediction Extractor Function ===
def extract_predictions(text):
    pattern = r'\b(?:\d{1,2}:\d{2})?\s?[A-Za-z\s]+\s+vs\s+[A-Za-z\s]+.*?(?:Over|Under|BTTS|Win|Draw|Handicap).*'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches

# === Fetch Predictions From Telegram ===
def get_telegram_predictions():
    predictions = []

    with client:
        for channel in channels:
            for message in client.iter_messages(channel, limit=30):
                if message.text:
                    picks = extract_predictions(message.text)
                    predictions.extend(picks)

    return predictions

# === Optional: Run Script Directly ===
if __name__ == '__main__':
    results = get_telegram_predictions()
    for i, pred in enumerate(results, 1):
        print(f"{i}. {pred}")
