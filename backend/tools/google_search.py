"""
Google Search Tool — Keyless Google News RSS and Wikipedia search aggregator.
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

def google_search(query: str, num_results: int = 5) -> str:
    """
    Search Google for the query. Returns structured results including titles and URLs.
    Does not require any third-party API keys or setup.
    """
    results = []
    
    # 1. Try Google News RSS Search (highly reliable, updated in real time)
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            count = 0
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                source = item.find("source").text if item.find("source") is not None else "Google News"
                
                # Clean up title if it contains source suffix (e.g., " - The Verge")
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title_clean = parts[0]
                else:
                    title_clean = title
                
                if title_clean and link:
                    results.append(f"Title: {title_clean}\nURL: {link}\nSource: {source}\n---")
                    count += 1
                    if count >= num_results:
                        break
    except Exception:
        pass
        
    if results:
        return "\n\n".join(results)
        
    # 2. Fallback to Wikipedia search if Google News returns nothing (for static/academic concepts)
    wiki_url = "https://en.wikipedia.org/w/api.php"
    wiki_params = {
        "action": "opensearch",
        "search": query,
        "limit": num_results,
        "namespace": 0,
        "format": "json"
    }
    wiki_headers = {
        "User-Agent": "AgenticAISearchTool/1.0 (ganeshdhogale@gmail.com) Python-requests/2.31.0"
    }
    
    try:
        wiki_response = requests.get(wiki_url, params=wiki_params, headers=wiki_headers, timeout=10)
        if wiki_response.status_code == 200:
            data = wiki_response.json()
            titles = data[1]
            links = data[3]
            for i in range(min(len(titles), num_results)):
                results.append(f"Title: {titles[i]} (Wikipedia)\nURL: {links[i]}\nSource: Wikipedia\n---")
    except Exception:
        pass
        
    if results:
        return "\n\n".join(results)
        
    return "No web search results found."
