from playwright.sync_api import sync_playwright

def scrape_blog_predictions(url, keywords=['over', 'goal', 'correct score']):
    predictions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        browser.close()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    for tag in soup.find_all(['p', 'div', 'span']):
        text = tag.get_text().strip()
        if any(k in text.lower() for k in keywords):
            predictions.append(text)

    return predictions
