# crawler/explore_sitemap_index.py

import requests
from bs4 import BeautifulSoup

def get_all_sitemaps(index_url="https://www.tasteofhome.com/sitemap_index.xml"):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(index_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to load sitemap index: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "xml")
    sitemap_links = [loc.text for loc in soup.find_all("loc")]
    return sitemap_links

if __name__ == "__main__":
    all_sitemaps = get_all_sitemaps()
    print(f"🔎 Found {len(all_sitemaps)} sitemaps:")
    for sm in all_sitemaps:
        print(sm)
