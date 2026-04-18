import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://www.petmd.com/dog/emergency/poisoning-toxicity"
BASE_URL = "https://www.petmd.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def is_article(url: str) -> bool:
    """
    Heuristic:
    - Must be /dog/
    - Must have at least 3 path parts after domain (real article depth)
    - Reject known hub patterns
    """
    if not url.startswith("https://www.petmd.com/dog/"):
        return False

    path = url.replace("https://www.petmd.com", "")
    parts = [p for p in path.split("/") if p]

    # Must be deeper than /dog/<section>/<article>
    if len(parts) < 3:
        return False

    # Reject known hub-style pages
    hub_keywords = ["medications", "breeds", "nutrition", "care", "behavior"]
    if len(parts) == 2 and parts[1] in hub_keywords:
        return False

    return True


def fetch_articles():
    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    articles = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(BASE_URL, href)

        if is_article(full_url):
            articles.add(full_url.rstrip("/"))

    return sorted(articles)


def save_file(links, filename="petmd_dog_articles_clean.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Saved {len(links)} clean article URLs → {filename}")


if __name__ == "__main__":
    links = fetch_articles()
    save_file(links)