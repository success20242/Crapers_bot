import os
import re
import time
import logging
import requests
import json
import pathlib
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from telegram import Bot
from telethon.sync import TelegramClient
from telethon.tl.types import User

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or 'YOUR_CHAT_ID'

if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN' or TELEGRAM_CHAT_ID == 'YOUR_CHAT_ID':
    logging.warning("⚠️ Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your environment or .env file!")

api_id = 21993597
api_hash = '3648f9e2efb3e88365a954ecbbf987c5'

logging.basicConfig(level=logging.INFO)

telegram_channels = [
    '@FreeDailyBettingTips',
    '@aimbetofficial',
    '@LoyalTipsters02',
    '@Suretips_01',
    '@Andison345',
    '@EPOddsSupportBot',
    '@epPay_afterbot'
]

blog_urls = [
    "https://betensured.com/predictions",
    "https://www.sportybetpredict.com/",
    "https://www.surebet247.com/blog",
    "https://www.soccerpunter.com/",
    "https://www.bettingtips1x2.com/",
    "https://www.freesupertips.com/football-predictions/",
    "https://www.windrawwin.com/",
    "https://www.betloy.com/predictions",
    "https://tips180.com/",
    "https://betimate.com/",
    "https://www.zulubet.com/",
    "https://www.forebet.com/",
    "https://www.betfame.com/tips/",
    "https://www.bettingclosed.com/predictions",
    "https://www.vitibet.com/"
]

VALID_TIPS = [
    "1", "X", "2", "1X", "X2", "12",
    "Over 2.5", "Under 2.5", "GG", "NG",
    "Home Win", "Away Win", "Draw"
]

KEYWORDS = {
    'correct score': 3,
    'over': 2,
    'under': 2,
    'btts': 2,
    'goal': 1,
    'draw': 1,
    'home': 1,
    'away': 1,
    'win': 1,
    'handicap': 2
}

PREDICTION_PATTERN = re.compile(r'(over|under|btts|draw|win|handicap|gg|ng|1x|x2|12|correct score|1|x|2)', re.IGNORECASE)

def extract_predictions(text):
    has_tip = bool(re.search(PREDICTION_PATTERN, text))
    has_teams = len(re.findall(r'\b[A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})?\b', text)) >= 2
    return has_tip and has_teams

def looks_like_match_line(text):
    return any(sep in text.lower() for sep in [' vs ', ' - ', ' v ', ' @ '])

def get_telegram_predictions():
    results = []
    today = datetime.now(timezone.utc).date()
    with TelegramClient('session_name', api_id, api_hash) as client:
        for channel in telegram_channels:
            try:
                entity = client.get_entity(channel)
                if isinstance(entity, User):
                    logging.info(f"🔍 Skipping bot or user: {channel}")
                    continue
                for message in client.iter_messages(channel, limit=100):
                    if message.date.date() == today and message.text:
                        if extract_predictions(message.text) and looks_like_match_line(message.text):
                            score = sum(KEYWORDS[k] for k in KEYWORDS if k in message.text.lower())
                            results.append((message.text.strip(), score))
            except Exception as e:
                logging.warning(f"Failed to fetch messages from {channel}: {e}")
    return results

def scrape_blog_predictions(url):
    predictions = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            page = browser.new_page()
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all(['p', 'div', 'span', 'li']):
            text = tag.get_text().strip()
            if len(text) > 10 and extract_predictions(text) and looks_like_match_line(text):
                score = sum(KEYWORDS[k] for k in KEYWORDS if k in text.lower())
                predictions.append((text, score))

    except Exception as e:
        logging.warning(f"❌ Error scraping {url}: {e}")
    return predictions

TOP_PREDICTIONS_LIMIT = 30

def collect_all_predictions():
    combined_predictions = []

    logging.info("📥 Scraping blog/forum URLs...")
    for url in blog_urls:
        logging.info(f"🔗 {url}")
        site_preds = scrape_blog_predictions(url)
        combined_predictions.extend(site_preds)
        time.sleep(2)

    logging.info("📥 Scraping Telegram channels...")
    telegram_preds = get_telegram_predictions()
    combined_predictions.extend(telegram_preds)

    seen = set()
    unique = []
    for text, score in combined_predictions:
        if text not in seen and 10 < len(text) < 400:
            seen.add(text)
            unique.append((text, score))

    return sorted(unique, key=lambda x: x[1], reverse=True)[:TOP_PREDICTIONS_LIMIT]

def save_predictions_to_file(predictions, filename=None):
    pathlib.Path("data").mkdir(exist_ok=True)
    filename = filename or f"data/predictions_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([{'text': text, 'score': score} for text, score in predictions], f, indent=2, ensure_ascii=False)
    logging.info(f"💾 Saved predictions to {filename}")

def format_for_telegram(predictions):
    header = f"\U0001F4CA *Top Football Predictions - {datetime.now().strftime('%b %d')}*\n\n"
    body = ""
    for i, (text, score) in enumerate(predictions, 1):
        body += f"{i}. _({score})_ {text}\n"
    return header + body

def post_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': chunk,
            'parse_mode': 'Markdown'
        }
        try:
            res = requests.post(url, json=payload)
            logging.info(f"📤 Posted to Telegram. Status: {res.status_code}")
        except Exception as e:
            logging.error(f"❌ Telegram post failed: {e}")

def run_automation():
    all_predictions = collect_all_predictions()
    if all_predictions:
        save_predictions_to_file(all_predictions)
        message = format_for_telegram(all_predictions)
        post_to_telegram(message)
    else:
        logging.info("No predictions collected.")

if __name__ == '__main__':
    run_automation()
