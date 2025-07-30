import requests
from bs4 import BeautifulSoup
import json

with open('config.json') as f:
    config = json.load(f)

def fetch_web_predictions():
    predictions = []

    for url in config['blogs'] + config['forums']:
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            texts = soup.find_all(['p', 'li', 'span'])

            for tag in texts:
                line = tag.get_text(strip=True)
                if "vs" in line.lower() or "over" in line.lower():
                    predictions.append(line)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return predictions
