# crawler/sitemap_parser.py

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_recipe_sitemap_links(index_url="https://www.tasteofhome.com/sitemap_index.xml"):
    """Get all recipe-sitemap URLs from the index."""
    response = requests.get(index_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")
    all_sitemaps = [loc.text for loc in soup.find_all("loc")]
    recipe_sitemaps = [url for url in all_sitemaps if "recipe-sitemap" in url]
    return recipe_sitemaps

def extract_urls_from_sitemap(sitemap_url):
    """Extract recipe URLs from a given sitemap XML."""
    response = requests.get(sitemap_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")
    return [loc.text for loc in soup.find_all("loc")]

def extract_all_recipe_urls(limit=100):
    recipe_urls = []
    for sitemap in get_recipe_sitemap_links()[:3]:
        urls = extract_urls_from_sitemap(sitemap)
        # Filter: must start with /recipes/ and NOT be an image
        urls = [u for u in urls if "/recipes/" in u and not u.endswith((".jpg", ".png", ".jpeg"))]
        recipe_urls.extend(urls)
        if len(recipe_urls) >= limit:
            break
    return recipe_urls[:limit]


# Test
if __name__ == "__main__":
    urls = extract_all_recipe_urls()
    print(f"✅ Found {len(urls)} recipe URLs.")
    for u in urls[:5]:
        print(u)
