import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://www.petmd.com/dog/breeds"
BASE_URL = "https://www.petmd.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_breed_links():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    breed_links = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.startswith("/dog/breeds/") and href != "/dog/breeds":
            full_url = urljoin(BASE_URL, href)
            breed_links.add(full_url)

    return sorted(breed_links)


def save_links(links, filename="petmd_dog_breeds.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        print(f"Saved {len(links)} links to {filename}")
    except IOError as e:
        print(f"Error writing file: {e}")


def main():
    links = fetch_breed_links()
    if links:
        save_links(links)


if __name__ == "__main__":
    main()