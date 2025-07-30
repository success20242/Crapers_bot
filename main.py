from telegram_scraper import fetch_telegram_predictions  # or get_telegram_predictions
from web_scraper import fetch_web_predictions  # or scrape_blog_predictions
from utils import clean_predictions
from datetime import datetime
import requests
import json

# === Load Configuration ===
with open('config.json') as f:
    config = json.load(f)

TELEGRAM_BOT_TOKEN = config['telegram_bot_token']
TELEGRAM_CHANNEL_ID = config['telegram_post_channel']

# === Send Message to Telegram ===
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Posted to Telegram.")
    else:
        print(f"❌ Telegram post failed: {response.text}")

# === Main Function ===
def run():
    print("🔄 Fetching Telegram predictions...")
    telegram_preds = fetch_telegram_predictions()

    print("🔄 Fetching web predictions...")
    blog_preds = fetch_web_predictions()

    print("🧹 Cleaning and merging predictions...")
    combined_preds = clean_predictions(telegram_preds + blog_preds)
    final_predictions = list(set(combined_preds))[:50]

    if final_predictions:
        today = datetime.now().strftime('%Y-%m-%d')
        telegram_message = f"⚽️ <b>Today's Top Football Predictions ({today}):</b>\n\n"
        telegram_message += "\n".join(f"• {p}" for p in final_predictions[:15])  # send top 15

        print("📤 Sending to Telegram...")
        send_to_telegram(telegram_message)
    else:
        print("❌ No predictions found.")

# === Entry Point ===
if __name__ == "__main__":
    run()
