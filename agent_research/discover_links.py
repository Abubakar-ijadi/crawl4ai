"""Use crawl4ai (this repo) to read the Florida DFS Bulk Download page and list the CSV links."""
import asyncio, json, re, sys
URL = "https://licenseesearch.fldfs.com/BulkDownload"

async def with_crawl4ai():
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    async with AsyncWebCrawler() as crawler:
        r = await crawler.arun(URL, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
        links = [l["href"] for l in r.links.get("external", []) + r.links.get("internal", [])]
        return [l for l in links if l.lower().endswith(".csv")]

def with_requests():
    import requests
    h = requests.get(URL, timeout=60, headers={"User-Agent": "Mozilla/5.0"}).text
    return sorted(set(re.findall(r'https://www\.myfloridacfo\.com/downloads/[^"\']+?\.csv', h)))

import os
os.makedirs(os.path.dirname(sys.argv[1]) or ".", exist_ok=True)
links = []
try:
    links = asyncio.run(with_crawl4ai()); print("crawl4ai found", len(links), "csv links")
except Exception as e:
    print("crawl4ai failed, falling back to requests:", e)
if not links:
    links = with_requests()
json.dump(sorted(set(links)), open(sys.argv[1], "w"), indent=1)
print("\n".join(links))
