import requests
from bs4 import BeautifulSoup
import os, re


def url_to_filename(url: str) -> str:
    """Converts a URL to a clean filename."""
    # strip protocol and domain
    path = url.replace('https://', '').replace('http://', '')
    # replace special chars with underscores
    clean = re.sub(r'[^a-z0-9]', '_', path.lower())
    # remove consecutive underscores
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:80] + '.txt'   # cap filename length

def save_article(text: str, url: str, output_dir: str):
    """save article to directory with url and article text"""
    filename = url_to_filename(url)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"SOURCE: {url}\n\n")
        f.write(text)
    return filepath

def scrape_article(url: str) -> str:
    """
    Scrapes and extracts main article text from articles. Fetches one URL and returns clean article text.
    Strips nav, footer, scripts to get clean body text only.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; portfolio bot)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # strip everything that isn't article content
        for tag in soup(['nav','footer','script','style','header','aside']):
            tag.decompose()
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])

        # remove very short paragraphs (navigation remnants, ads)
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        return '. '.join(sentences)
    except Exception as e:
        print(f"Failed: {url} — {e}")
        return ''

def scrape_all(urls_file: str) -> int:
    """
    Go thru all urls in articles_urls.txt to get the urls 
    """
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip()]
    articles = 0
    os.makedirs('data/articles', exist_ok=True)
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/{len(urls)}: {url}")
        text = scrape_article(url)
        if len(text) > 300:
            filepath = save_article(text, url, 'data/articles')
            print(f"  → saved to {filepath}")
        articles = articles + 1

    return articles



if __name__ == '__main__':
    import json, os
    articles = scrape_all('article_urls.txt')
    print(f"\nScraped {articles} articles successfully")



# TODO-IMPROVE: could clean up the article scraping since theres words meshed together 
# + random u/2019 characters in there but thats a later problem if it rly comes up
