import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import time
from googlesearch import search

PAGESPEED_API_KEY = "AIzaSyCsVrxyA-YPLBssJqdDlFJ4Bc3Y_IC34dc"


def get_page_speed(url, strategy):
    try:
        endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={PAGESPEED_API_KEY}"
        response = requests.get(endpoint)
        data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        score = int(lighthouse.get("categories", {}).get("performance", {}).get("score", 0) * 100)
        audits = lighthouse.get("audits", {})

        fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
        lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
        return score, fcp, lcp
    except Exception as e:
        return "Error", "Error", "Error"


def analyze_competitors(keyword):
    results = []
    urls = []

    try:
        for url in search(keyword, num_results=20):
            if "facebook.com" in url or "linkedin.com" in url:
                continue
            urls.append(url)
            if len(urls) == 10:
                break
    except Exception as e:
        print("Google search error:", e)
        return pd.DataFrame()

    for url in urls:
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string.strip() if soup.title else "No title"
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and meta_tag.get("content"):
                meta_desc = meta_tag["content"]
            else:
                meta_desc = "No meta description"

            h1 = soup.find("h1")
            h1_text = h1.get_text(strip=True) if h1 else "No H1 tag"

            word_count = len(soup.get_text(" ").split())

            schema = "Yes" if "application/ld+json" in response.text else "No"

            internal_links = len([a for a in soup.find_all("a", href=True) if url in a["href"]])
            external_links = len([a for a in soup.find_all("a", href=True) if url not in a["href"] and "http" in a["href"]])

            images = soup.find_all("img")
            total_imgs = len(images)
            alt_imgs = len([img for img in images if img.get("alt")])
            alt_ratio = round((alt_imgs / total_imgs) * 100, 2) if total_imgs > 0 else 0

            # Google PageSpeed Insights API
            mobile_score, mobile_fcp, mobile_lcp = get_page_speed(url, "mobile")
            desktop_score, desktop_fcp, desktop_lcp = get_page_speed(url, "desktop")

            results.append({
                "Title": title,
                "URL": url,
                "Meta Description": meta_desc,
                "Top Keywords": "No keywords",
                "H1 Headline": h1_text,
                "Word Count": word_count,
                "Schema Markup": schema,
                "Internal Links": internal_links,
                "External Links": external_links,
                "Alt Text %": alt_ratio,
                "Mobile Score": mobile_score,
                "Mobile FCP": mobile_fcp,
                "Mobile LCP": mobile_lcp,
                "Desktop Score": desktop_score,
                "Desktop FCP": desktop_fcp,
                "Desktop LCP": desktop_lcp,
            })
            time.sleep(1)

        except Exception as e:
            print("Error analyzing", url, ":", e)
            continue

    df = pd.DataFrame(results)
    return df
