from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

# === Prediction Keywords ===
DEFAULT_KEYWORDS = ['over', 'goal', 'btts', 'win', 'draw', 'correct score', 'under', 'handicap']

# === Scrape a Single Blog URL ===
def scrape_blog_predictions(url, keywords=DEFAULT_KEYWORDS):
    predictions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"🌐 Scraping: {url}")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            content = page.content()

            soup = BeautifulSoup(content, 'html.parser')

            for tag in soup.find_all(['p', 'div', 'span']):
                text = tag.get_text().strip()
                if text and any(k in text.lower() for k in keywords):
                    predictions.append(text)

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        finally:
            browser.close()

    return predictions

# === Batch Scrape Multiple Blogs ===
def scrape_multiple_blogs(url_list, keywords=DEFAULT_KEYWORDS, save_to_json=False):
    all_predictions = []

    for url in url_list:
        preds = scrape_blog_predictions(url, keywords)
        all_predictions.extend(preds)

    # Remove duplicates & trim
    unique_predictions = list(set(all_predictions))[:100]

    if save_to_json:
        filename = f"blog_predictions_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unique_predictions, f, indent=2, ensure_ascii=False)
        print(f"📁 Saved to {filename}")

    return unique_predictions

# === Example Usage ===
if __name__ == '__main__':
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

    predictions = scrape_multiple_blogs(blog_urls, save_to_json=True)

    print(f"\n✅ Total Predictions Collected: {len(predictions)}")
    for i, p in enumerate(predictions[:10], 1):
        print(f"{i}. {p}")
