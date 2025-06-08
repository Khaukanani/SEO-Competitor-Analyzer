import requests

# ✅ Replace these with your real values
API_KEY = "AIzaSyBpQDLtmqi86XLArhpyFPYqvyLMgnqcALE"
SEARCH_ENGINE_ID = "54aed0462cfd84ae5"  # ✅ Corrected value here

# 🔍 The search term
query = "phone and laptop repair Polokwane"

def google_search(query, api_key, cse_id, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
    }

    response = requests.get(url, params=params)

    # 🔍 Add this line to show the raw API response (for debugging)
    print("🔍 RAW RESPONSE:\n", response.json())

    results = response.json().get("items", [])

    competitors = []
    for result in results:
        title = result.get("title")
        link = result.get("link")
        competitors.append((title, link))
    
    return competitors

# ▶️ Run the search
competitor_list = google_search(query, API_KEY, SEARCH_ENGINE_ID)

# 📋 Print the results
print("\nTop 10 Competitors:\n")
for i, (title, link) in enumerate(competitor_list, start=1):
    print(f"{i}. {title}\n   {link}\n")
import csv

# 💾 Save to CSV
with open("top_10_competitors.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "URL"])  # Header
    for title, link in competitor_list:
        writer.writerow([title, link])

print("✅ Saved to top_10_competitors.csv")
