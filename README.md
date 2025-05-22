🧠 TasteOfHome Web Crawler – MSA University

 🎯 Overview

A smart web crawler and analytics dashboard built for the TasteOfHome recipe website. It extracts structured recipe data, analyzes crawlability, and visualizes insights using **Streamlit**.

---

📁 Project Structure

- `app.py` – Streamlit dashboard
- `content_extractor.py` – Scrapes recipe details (Selenium + BeautifulSoup)
- `crawlability_checker.py` – Parses robots.txt
- `sitemap_parser.py` – Extracts recipe URLs from sitemaps
- `explore_sitemap_index.py` – Finds all sitemap files
- `recipes.json` – Collected recipe data
- `requirements.txt` – Dependencies

---

🧪 Features

- Crawlability analysis (robots.txt, delays, sitemaps)
- JS-handled scraping using Selenium
- Recipe data extraction (title, ingredients, steps, etc.)
- Streamlit dashboard with interactive visuals
- Keyword and complexity analysis

---

🚀 How to Run

bash
pip install -r requirements.txt
streamlit run app.py
