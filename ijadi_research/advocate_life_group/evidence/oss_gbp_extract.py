"""Open-source GBP + review extraction for Google Maps pages.

Fetch layer: the container's egress policy blocks google.com, so pages were fetched as
rendered HTML by Firecrawl (rawHtml). All scraping/parsing here is open source:
  * crawl4ai (Apache-2.0) JsonCssExtractionStrategy over `raw:` HTML for search-result cards
  * BeautifulSoup4 (MIT) for place-panel fields, star histogram, top reviews, owner replies

Usage:
  python3 oss_gbp_extract.py search <label> <query> <html> [<label> <query> <html> ...] --out search.json
  python3 oss_gbp_extract.py place  <label> <html> [<label> <html> ...] --out places.json
"""
import asyncio, json, re, sys
from urllib.parse import unquote
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

CARD_SCHEMA = {
    "name": "maps_result_cards",
    "baseSelector": "div[role='feed'] div[role='article']",
    "fields": [
        {"name": "name", "selector": "a.hfpxzc", "type": "attribute", "attribute": "aria-label"},
        {"name": "href", "selector": "a.hfpxzc", "type": "attribute", "attribute": "href"},
        {"name": "rating", "selector": "span.MW4etd", "type": "text"},
        {"name": "reviews", "selector": "span.UY7F9", "type": "text"},
        {"name": "lines", "selector": "div.W4Efsd", "type": "list", "fields": [{"name": "t", "type": "text"}]},
        {"name": "phone", "selector": "span.UsdlK", "type": "text"},
        {"name": "sponsored", "selector": "span.jHLihd", "type": "text"},
    ],
}


def feature_id(href):
    m = re.search(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)", href or "")
    return m.group(1) if m else None


def to_int(s):
    m = re.search(r"[\d,]+", s or "")
    return int(m.group(0).replace(",", "")) if m else None


async def parse_search(items):
    out = []
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        for label, query, path in items:
            html = open(path, encoding="utf-8").read()
            cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=JsonCssExtractionStrategy(CARD_SCHEMA))
            r = await c.arun(url="raw:" + html, config=cfg)
            cards = json.loads(r.extracted_content or "[]")
            seen, rows = set(), []
            for rank, cd in enumerate(cards, 1):
                fid = feature_id(cd.get("href"))
                if not cd.get("name") or fid in seen:
                    continue
                seen.add(fid)
                lines = [x.get("t", "") for x in cd.get("lines") or [] if x.get("t")]
                cand = [l for l in lines if "·" in l and not re.match(r"^\s*(\d\.\d|No reviews|Open|Closed|Closes|Opens)", l)]
                first = min(cand, key=len) if cand else ""
                parts = [p.strip() for p in first.split("·") if p.strip()]
                rows.append({
                    "rank": len(rows) + 1,
                    "name": cd["name"],
                    "rating": float(cd["rating"]) if cd.get("rating") else None,
                    "reviews": to_int(cd.get("reviews")),
                    "category": parts[0] if parts else None,
                    "address": parts[-1] if len(parts) > 1 else None,
                    "phone": cd.get("phone"),
                    "sponsored": bool(cd.get("sponsored")),
                    "feature_id": fid,
                    "place_url": (cd.get("href") or "").split("?")[0],
                })
            out.append({"label": label, "query": query, "crawl4ai_success": r.success, "results": rows})
            print(f"{label}: {len(rows)} places", file=sys.stderr)
    return out


def parse_place(label, path):
    h = open(path, encoding="utf-8").read()
    s = BeautifulSoup(h, "html.parser")
    name = next((x.get_text(strip=True) for x in s.find_all("h1") if x.get_text(strip=True)), None)
    hist = {}
    for tr in s.select("tr[aria-label]"):
        m = re.match(r"(\d) stars?, ([\d,]+) reviews?", tr["aria-label"])
        if m:
            hist[int(m.group(1))] = int(m.group(2).replace(",", ""))
    total = sum(hist.values()) or None
    avg_el = s.select_one(".fontDisplayLarge")
    items = {e.get("data-item-id"): (e.get("aria-label") or e.get_text(" ", strip=True)).strip() for e in s.select("[data-item-id]")}
    reviews = []
    for blk in s.select("div.jftiEf"):
        rid = blk.get("data-review-id")
        stars = blk.select_one("span.kvMYJc")
        txt = blk.select_one("span.wiI7pd")
        reply = blk.select_one("div.CDe7pd")
        reviews.append({
            "id": rid,
            "reviewer": (blk.select_one(".d4r55") or {}).get_text(strip=True) if blk.select_one(".d4r55") else None,
            "stars": to_int(stars.get("aria-label")) if stars and stars.get("aria-label") else len((stars.get_text() if stars else "").split()),
            "when": blk.select_one(".rsqaWe").get_text(strip=True) if blk.select_one(".rsqaWe") else None,
            "text": txt.get_text(" ", strip=True)[:400] if txt else "",
            "owner_reply": bool(reply),
            "owner_reply_when": (re.search(r"Response from the owner\s+(.*? ago)", reply.get_text(" ", strip=True)) or [None, None])[1] if reply else None,
        })
    hours_row = s.select_one('[aria-label*="Copy open hours"]')
    return {
        "label": label,
        "name": name,
        "category": (s.select_one("button.DkEaL") or s.select_one(".DkEaL")).get_text(strip=True) if (s.select_one(".DkEaL")) else None,
        "rating": float(avg_el.get_text(strip=True)) if avg_el and re.match(r"^\d(\.\d)?$", avg_el.get_text(strip=True)) else None,
        "total_reviews_histogram": total,
        "star_histogram": hist,
        "address": next((v.replace("Address:", "").strip() for k, v in items.items() if k == "address"), None),
        "phone": next((v.replace("Phone:", "").strip() for k, v in items.items() if k and k.startswith("phone")), None),
        "website": next((v.replace("Website:", "").strip() for k, v in items.items() if k == "authority"), None),
        "booking_link": next((v for k, v in items.items() if k and k.startswith("action:")), None),
        "has_hours": bool(hours_row) or "Show open hours" in h,
        "owner_updates_present": "From the owner" in h,
        "unclaimed": ("Claim this business" in h) or ("Own this business?" in h),
        "top_reviews_visible": reviews,
        "top_reviews_with_owner_reply": sum(r["owner_reply"] for r in reviews),
    }


if __name__ == "__main__":
    mode, args = sys.argv[1], sys.argv[2:]
    out_path = args[args.index("--out") + 1]
    args = args[: args.index("--out")]
    if mode == "search":
        trip = [tuple(args[i:i + 3]) for i in range(0, len(args), 3)]
        data = asyncio.run(parse_search(trip))
    else:
        data = [parse_place(args[i], args[i + 1]) for i in range(0, len(args), 2)]
    json.dump(data, open(out_path, "w"), indent=1)
