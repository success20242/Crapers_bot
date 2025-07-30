from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import time

# === CONFIGURATION ===
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
    'correct score': 3,
    'over': 2,
    'under': 2,
    'btts': 2,
    'goal': 1,
    'draw': 1,
    'home': 1,
    'away': 1
}

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

# === SCRAPER ===
def scrape_predictions(url):
    predictions = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, 'html.parser')

        for tag in soup.find_all(['p', 'div', 'span']):
            text = tag.get_text().strip()
            if any(k in text.lower() for k in KEYWORDS):
                score = sum(KEYWORDS[k] for k in KEYWORDS if k in text.lower())
                predictions.append((text, score))

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return predictions

# === FORMAT + POST ===
def format_predictions(predictions_by_site):
    message = f"📊 *Today’s Football Predictions*\n\n"

    for site, preds in predictions_by_site.items():
        message += f"🌐 *{site}*\n"
        if preds:
            for text, score in sorted(preds, key=lambda x: x[1], reverse=True)[:5]:
                message += f"🔹 _({score})_ {text}\n"
        else:
            message += "❌ No valid predictions found.\n"
        message += "\n"

    return message

def post_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Telegram Response: {res.status_code}")
    except Exception as e:
        print(f"Telegram post failed: {e}")

# === MAIN ===
if __name__ == "__main__":
    all_predictions = {}

    for url in BLOG_URLS:
        print(f"Scraping: {url}")
        preds = scrape_predictions(url)
        domain = url.split("//")[-1].split("/")[0]
        all_predictions[domain] = preds
        time.sleep(3)  # polite delay between sites

    if all_predictions:
        message = format_predictions(all_predictions)
        print("\nPosting to Telegram...\n")
        post_to_telegram(message)
    else:
        print("No predictions gathered.")
