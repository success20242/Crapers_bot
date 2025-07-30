from telegram_scraper import fetch_telegram_predictions
from web_scraper import fetch_web_predictions
from utils import clean_predictions
import json
import requests

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Function to post message to Telegram channel
def send_to_telegram(text):
    token = config['telegram_bot_token']
    channel = config['telegram_post_channel']
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": channel,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Posted to Telegram successfully.")
    else:
        print(f"❌ Telegram post failed: {response.text}")

# Main logic
if __name__ == '__main__':
    print("🔍 Scraping Telegram...")
    t_preds = fetch_telegram_predictions()

    print("🔍 Scraping Blogs/Forums...")
    w_preds = fetch_web_predictions()

    all_preds = clean_predictions(t_preds + w_preds)

    if all_preds:
        message = "⚽️ <b>Today's Top Football Predictions:</b>\n\n"
        message += "\n".join(f"• {line}" for line in all_preds[:15])
        send_to_telegram(message)
    else:
        print("❌ No predictions found.")
