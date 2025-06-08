import requests
import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

# === CONFIGURATION ===
API_KEY = "AIzaSyBpQDLtmqi86XLArhpyFPYqvyLMgnqcALE"
SEARCH_ENGINE_ID = "54aed0462cfd84ae5"
query = "phone and laptop repair Polokwane"
driver_path = "C:/Users/klawr/Documents/SEO Projects/SEO APP/chromedriver.exe"
save_path = "C:/Users/klawr/Documents/SEO Projects/SEO APP/competitors_data.csv"
pages_to_scrape = 2  # For pagination (10 results per page)

# === GOOGLE CUSTOM SEARCH ===
def google_search(query, api_key, cse_id, num_results=10, start_index=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
        "start": start_index
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    return [(item.get("title", "No title"), item.get("link", "")) for item in items]

# === PAGESPEED INSIGHTS ===
def get_pagespeed_data(url):
    try:
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}&strategy=mobile"
        response = requests.get(api_url)
        data = response.json()

        lighthouse = data["lighthouseResult"]
        performance_score = int(lighthouse["categories"]["performance"]["score"] * 100)
        fcp = lighthouse["audits"]["first-contentful-paint"]["displayValue"]
        lcp = lighthouse["audits"]["largest-contentful-paint"]["displayValue"]

        return performance_score, fcp, lcp
    except:
        return "N/A", "N/A", "N/A"

# === SCRAPER ===
def get_meta_info(url, driver):
    try:
        driver.get(url)
        time.sleep(3)

        # Title
        title = driver.title or "No title"

        # Meta description
        meta_desc = "No meta description"
        for selector in ["//meta[@name='description']", "//meta[@property='og:description']", "//meta[@name='twitter:description']"]:
            try:
                meta_desc = driver.find_element(By.XPATH, selector).get_attribute("content") or meta_desc
                if meta_desc != "No meta description":
                    break
            except:
                pass

        # Keywords
        try:
            keywords = driver.find_element(By.XPATH, "//meta[@name='keywords']").get_attribute("content") or "No keywords"
        except:
            keywords = "No keywords"

        # H1
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1").text.strip() or "No H1 tag"
        except:
            h1 = "No H1 tag"

        # Word count
        try:
            word_count = len(driver.find_element(By.TAG_NAME, "body").text.split())
        except:
            word_count = 0

        # Schema markup check
        schema = "Yes" if any("application/ld+json" in s.get_attribute("type") for s in driver.find_elements(By.TAG_NAME, "script")) else "No"

        # Internal and external links
        links = driver.find_elements(By.TAG_NAME, "a")
        internal, external = 0, 0
        domain = urlparse(url).netloc
        for link in links:
            try:
                href = link.get_attribute("href") or ""
                if domain in href:
                    internal += 1
                elif href.startswith("http"):
                    external += 1
            except:
                continue

        # Image alt ratio
        images = driver.find_elements(By.TAG_NAME, "img")
        with_alt = sum(1 for img in images if img.get_attribute("alt"))
        alt_ratio = round((with_alt / len(images)) * 100, 2) if images else 0

        return title, url, meta_desc, keywords, h1, word_count, schema, internal, external, alt_ratio

    except Exception as e:
        return "Failed", url, str(e), "N/A", "N/A", 0, "N/A", 0, 0, 0

# === MAIN PROCESS ===
def main():
    print("🔍 Starting advanced SEO competitor analysis...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    all_data = [("Title", "URL", "Meta Description", "Top Keywords", "H1 Headline", "Word Count", "Schema Markup", "Internal Links", "External Links", "Alt Text %", "Mobile Score", "FCP", "LCP")]

    for i in range(pages_to_scrape):
        start = i * 10 + 1
        print(f"\n🔎 Fetching results {start} to {start+9}...")
        try:
            results = google_search(query, API_KEY, SEARCH_ENGINE_ID, start_index=start)
        except Exception as e:
            print(f"❌ Error with Google Search API: {e}")
            break

        for title, url in results:
            print(f"🌐 Processing: {url}")
            if "facebook.com" in url:
                print("⏭️ Skipping Facebook URL")
                all_data.append(("Skipped (Facebook)", url, "Skipped", "Skipped", "Skipped", "Skipped", "Skipped", 0, 0, 0, "Skipped", "Skipped", "Skipped"))
                continue

            meta_data = get_meta_info(url, driver)
            speed_data = get_pagespeed_data(url)

            all_data.append(meta_data + speed_data)

    driver.quit()

    # Save to CSV
    try:
        if os.path.exists(save_path):
            os.rename(save_path, save_path)  # Check if locked
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(all_data)
        print(f"\n✅ Data saved to: {save_path}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

if __name__ == "__main__":
    main()
