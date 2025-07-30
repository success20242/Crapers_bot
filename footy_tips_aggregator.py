import os
import re
import json
import asyncio
import logging
import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from playwright.async_api import async_playwright
import telegram

# === Load Environment Variables ===
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID") or 21993597)
API_HASH = os.getenv("TELEGRAM_API_HASH") or '3648f9e2efb3e88365a954ecbbf987c5'
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION") or None
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or 'YOUR_BOT_TOKEN'
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or 'YOUR_CHAT_ID'

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Constants ===
CHANNELS = [
    '@FreeDailyBettingTips',
    '@aimbetofficial',
    '@LoyalTipsters02',
    '@Suretips_01',
    '@Andison345',
    '@EPOddsSupportBot',
    '@epPay_afterbot'
]

BLOG_URLS = [
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

KEYWORDS = {
    "over 2.5": 5, "under 2.5": 5, "btts": 4, "draw": 3,
    "away win": 3, "home win": 3, "win": 2, "1x2": 2,
    "sure": 2, "tip": 2, "prediction": 2, "fixed": 2,
    "safe": 2, "gg": 3, "ng": 3, "ht/ft": 3
}

DATE_REGEX = r"\b(\d{1,2}[:.]\d{2})\b"
LEAGUE_REGEX = r"(Premier League|La Liga|Serie A|Bundesliga|Ligue 1|EPL|UCL|Championship|Friendly|Super League|MLS|Europa League|CAF|NPFL|USL|EFL)"

# === Prediction Extraction ===
def extract_predictions(text):
    predictions = []
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line.split()) < 3:
            continue
        if any(k in line.lower() for k in KEYWORDS):
            if re.search(DATE_REGEX, line) and re.search(LEAGUE_REGEX, line, re.IGNORECASE):
                score = sum(KEYWORDS[k] for k in KEYWORDS if k in line.lower())
                predictions.append((line, score))
    return predictions

def extract_from_raw_odds(text):
    odds_pattern = r'(\d{1,2}(?:\.\d{1,2})?)\s*(?:X)?\s*(\d{1,2}(?:\.\d{1,2})?)\s*(\d{1,2}(?:\.\d{1,2})?)'
    matches = re.findall(odds_pattern, text)
    results = []
    for match in matches:
        try:
            home, draw, away = map(float, match)
            result = "Home Win" if home < draw and home < away else "Draw" if draw < away else "Away Win"
            results.append((f"Inferred Tip: {result} (from odds {match[0]} X {match[1]} {match[2]})", 0))
        except:
            continue
    return results

# === Telegram Fetcher ===
async def get_telegram_predictions():
    predictions = []
    async with TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH) as client:
        today = datetime.datetime.now().date()
        for channel in CHANNELS:
            try:
                async for message in client.iter_messages(channel, limit=100):
                    if message.date.date() == today and message.text:
                        predictions += extract_predictions(message.text)
                        predictions += extract_from_raw_odds(message.text)
            except Exception as e:
                logging.warning(f"❌ Error fetching from {channel}: {e}")
    return predictions

# === Blog Scraper ===
async def scrape_blog_predictions(url):
    predictions = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)
            content = await page.content()
            await browser.close()
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all(['p', 'div', 'span']):
            text = tag.get_text().strip()
            if any(k in text.lower() for k in KEYWORDS):
                score = sum(KEYWORDS[k] for k in KEYWORDS if k in text.lower())
                if 10 < len(text) < 400:
                    predictions.append((text, score))
    except Exception as e:
        logging.warning(f"❌ Error scraping {url}: {e}")
    return predictions

# === Format Telegram Message ===
def format_for_telegram(predictions):
    header = f"📊 *Top Football Predictions - {datetime.datetime.now().strftime('%b %d')}*\n\n"
    body = ""
    for i, (text, score) in enumerate(predictions, 1):
        if "Inferred Tip" not in text:
            body += f"{i}. _({score})_ {text}\n"
    return header + body

# === Post to Telegram ===
async def post_to_telegram(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        logging.info("📤 Posted to Telegram successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to post to Telegram: {e}")

# === Save JSON ===
def save_predictions(predictions):
    os.makedirs("data", exist_ok=True)
    filename = f"data/predictions_{datetime.datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    logging.info(f"💾 Saved predictions to {filename}")

# === Main Runner ===
async def main():
    telegram_preds = await get_telegram_predictions()
    blog_preds = []
    for url in BLOG_URLS:
        blog_preds += await scrape_blog_predictions(url)
        await asyncio.sleep(1)  # avoid overloading

    combined = telegram_preds + blog_preds
    unique = list({p[0]: p for p in combined if len(p[0]) > 10 and "Inferred Tip" not in p[0]}.values())
    top = sorted(unique, key=lambda x: x[1], reverse=True)[:30]
    save_predictions(top)
    message = format_for_telegram(top)
    await post_to_telegram(message)

if __name__ == "__main__":
    asyncio.run(main())
