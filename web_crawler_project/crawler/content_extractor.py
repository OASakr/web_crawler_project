import os
import time
import json
import re
from collections import Counter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from sitemap_parser import extract_all_recipe_urls

def extract_recipe_data(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)
    time.sleep(3)  # Give JS time to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    def safe_get(selector, attr=None):
        el = soup.select_one(selector)
        if not el:
            return "N/A"
        return el.get(attr).strip() if attr and el.has_attr(attr) else el.get_text(strip=True)

    title       = safe_get("h1")
    description = safe_get("meta[name=description]", "content")

    # Image
    image_url = "N/A"
    img = soup.select_one("div.recipe-image img") \
          or soup.select_one("img.primary-image") \
          or soup.find("img")
    if img and img.has_attr("src"):
        image_url = img["src"]

    # Ingredients & instructions
    ingredients = [
        li.get_text(strip=True)
        for li in soup.select("ul.recipe-ingredients__list li")
        if li.get_text(strip=True)
    ]
    steps = [li.get_text(strip=True) for li in soup.select("li.recipe-directions__item")]
    if not steps:
        steps = [
            li.get_text(strip=True)
            for li in soup.find_all("li")
            if "step" in li.get("class", [])
        ]

    # Additional metadata
    rating     = safe_get("span.review-average")
    prep_time  = safe_get("span.prep-time")
    cook_time  = safe_get("span.cook-time")
    total_time = safe_get("span.total-time")

    # Nutrition
    nutrition = {}
    for item in soup.select("div.nutrition-section li"):
        text = item.get_text(strip=True)
        if ":" in text:
            key, val = [p.strip() for p in text.split(":", 1)]
            nutrition[key] = val

    # Categories / tags
    categories = [a.get_text(strip=True) for a in soup.select("a.category-link")]

    # Keyword extraction (simple)
    text_blob = description + " " + " ".join(steps)
    words = re.findall(r'\b\w+\b', text_blob.lower())
    stopwords = {
        "the","and","for","with","that","this","from","will","have","also",
        "when","which","your","more","make","them","their","just","than"
    }
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    common_keywords = [w for w, _ in Counter(filtered).most_common(10)]

    return {
        "url": url,
        "title": title,
        "description": description,
        "image_url": image_url,
        "ingredients": ingredients,
        "instructions": steps,
        "rating": rating,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "total_time": total_time,
        "nutrition": nutrition,
        "categories": categories,
        "keywords": common_keywords
    }

def batch_scrape_and_save(limit=100, output_path="data/recipes.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    recipe_urls = extract_all_recipe_urls(limit=limit)
    all_recipes = []

    for idx, url in enumerate(recipe_urls, start=1):
        print(f"🔄 Scraping [{idx}/{limit}]: {url}")
        data = extract_recipe_data(url)
        if data and data["ingredients"]:
            all_recipes.append(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(all_recipes)} recipes to {output_path}")

if __name__ == "__main__":
    batch_scrape_and_save()
