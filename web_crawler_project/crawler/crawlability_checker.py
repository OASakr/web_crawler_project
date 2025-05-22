# crawler/crawlability_checker.py
import requests
import requests

def analyze_robots_txt(url="https://www.tasteofhome.com/robots.txt"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch robots.txt (Status {response.status_code})"}

    lines = response.text.splitlines()
    disallowed = []
    allowed = []
    sitemaps = []
    crawl_delay = None

    for line in lines:
        line = line.strip()
        if line.startswith("Disallow"):
            disallowed.append(line.split(":")[1].strip())
        elif line.startswith("Allow"):
            allowed.append(line.split(":")[1].strip())
        elif line.lower().startswith("sitemap"):
            sitemaps.append(line.split(":", 1)[1].strip())
        elif line.lower().startswith("crawl-delay"):
            crawl_delay = line.split(":")[1].strip()

    return {
        "Allowed": allowed,
        "Disallowed": disallowed,
        "Sitemaps": sitemaps,
        "Crawl-Delay": crawl_delay
    }

if __name__ == "__main__":
    result = analyze_robots_txt()
    for k, v in result.items():
        print(f"{k}: {v}")

