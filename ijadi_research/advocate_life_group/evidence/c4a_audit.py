"""SEO/AEO/GEO page audit using crawl4ai.

Usage:
  python c4a_audit.py <label> <url_or_raw_html_path> [<label> <url_or_path> ...] --out out.json

If the second arg is a file path, the HTML is fed to crawl4ai via its `raw:` input
(used when the container's network policy blocks the host; HTML fetched by Firecrawl).
Otherwise crawl4ai fetches the URL itself with headless Chromium.
"""
import asyncio, json, os, re, sys
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

PHONE_RE = re.compile(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")
OH_ADDR_RE = re.compile(r"\d{2,6}[^<>\n]{3,60}?(?:OH|Ohio)\s*4\d{4}")


def jsonld_types(soup):
    types, blobs = [], []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "{}")
        except Exception:
            blobs.append("PARSE_ERROR")
            continue
        stack = [data]
        while stack:
            d = stack.pop()
            if isinstance(d, list):
                stack.extend(d)
            elif isinstance(d, dict):
                t = d.get("@type")
                if t:
                    types.extend(t if isinstance(t, list) else [t])
                stack.extend(v for v in d.values() if isinstance(v, (dict, list)))
    return sorted(set(types))


def analyze(label, src, html, result):
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["noscript"]):
        s.decompose()
    title = (soup.title.string or "").strip() if soup.title else ""
    md = soup.find("meta", attrs={"name": "description"})
    robots = soup.find("meta", attrs={"name": "robots"})
    canon = soup.find("link", rel="canonical")
    h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    h2 = [h.get_text(" ", strip=True) for h in soup.find_all("h2")]
    imgs = soup.find_all("img")
    no_alt = [i.get("src", "")[:90] for i in imgs if not (i.get("alt") or "").strip()]
    forms = []
    for f in soup.find_all("form"):
        fields = [
            (i.get("name") or i.get("id") or i.get("type") or "")
            for i in f.find_all(["input", "select", "textarea"])
            if i.get("type") not in ("hidden", "submit")
        ]
        forms.append({"action": f.get("action"), "fields": fields[:25]})
    text = soup.get_text(" ", strip=True)
    raw_lower = html.lower()
    md_text = (result.markdown.raw_markdown if result and result.markdown else "") or ""
    links = result.links if result else {"internal": [], "external": []}
    data = {
        "label": label,
        "source": src,
        "crawl4ai_success": bool(result and result.success),
        "html_bytes": len(html),
        "inline_style_bytes": sum(len(s.get_text()) for s in soup.find_all("style")),
        "script_tags": len(soup.find_all("script")),
        "title": title,
        "title_len": len(title),
        "meta_description": (md.get("content") or "").strip()[:300] if md else None,
        "meta_robots": robots.get("content") if robots else None,
        "canonical": canon.get("href") if canon else None,
        "viewport": bool(soup.find("meta", attrs={"name": "viewport"})),
        "h1": h1[:6],
        "h1_count": len(h1),
        "h2_sample": h2[:15],
        "h2_count": len(h2),
        "word_count_markdown": len(md_text.split()),
        "word_count_visible_text": len(text.split()),
        "internal_links": len(links.get("internal", [])),
        "external_links": len(links.get("external", [])),
        "external_link_domains": sorted({re.sub(r"^https?://(www\.)?", "", l.get("href", "")).split("/")[0] for l in links.get("external", [])})[:40],
        "jsonld_types": jsonld_types(soup),
        "microdata_types": sorted({t.get("itemtype") for t in soup.find_all(attrs={"itemtype": True})})[:10],
        "images": len(imgs),
        "images_missing_alt": len(no_alt),
        "forms": forms[:8],
        "phones": sorted(set(PHONE_RE.findall(text)))[:10],
        "oh_street_address_found": OH_ADDR_RE.findall(text)[:3],
        "tel_links": sorted({a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("tel:")})[:5],
        "has_faq_heading": bool(re.search(r"frequently asked|faq", text, re.I)),
        "question_headings": [h.get_text(" ", strip=True) for h in soup.find_all(["h2", "h3", "h4"]) if h.get_text().strip().endswith("?")][:12],
        "mentions_license_number": bool(re.search(r"licen[sc]e\s*(#|no\.?|number)", text, re.I)),
        "mentions_npn": bool(re.search(r"\bNPN\b", text)),
        "chat_widget": [k for k in ("intercom", "drift", "tawk", "livechat", "hubspot", "crisp", "podium", "birdeye", "zendesk", "tidio", "chatbot", "leadconnector", "gohighlevel") if k in raw_lower],
        "booking_widget": [k for k in ("calendly", "acuityscheduling", "youcanbook", "oncehub", "scheduleonce", "hubspot.com/meetings", "leadconnectorhq", "msgsndr", "timetrade", "booking") if k in raw_lower],
        "analytics": [k for k in ("gtag(", "googletagmanager", "google-analytics", "fbq(", "clarity.ms", "hotjar", "callrail") if k in raw_lower],
        "lorem_ipsum": raw_lower.count("lorem ipsum"),
        "placeholder_text": [p for p in ("insert link", "lorem ipsum", "your name here", "coming soon") if p in raw_lower],
        "recaptcha": "recaptcha" in raw_lower,
        "generator": (soup.find("meta", attrs={"name": "generator"}) or {}).get("content") if soup.find("meta", attrs={"name": "generator"}) else None,
        "keyword_hits": {k: len(re.findall(k, text, re.I)) for k in [
            "life insurance", "term life", "whole life", "final expense", "mortgage protection",
            "annuit", "medicare", "retirement", "long-term care", "ohio", "columbus", "mount vernon",
            "knox county", "licensed", "veteran", "federal", "IUL|indexed universal"]},
    }
    return data


async def main(pairs, out):
    results = []
    bcfg = BrowserConfig(headless=True, verbose=False)
    async with AsyncWebCrawler(config=bcfg) as crawler:
        for label, src in pairs:
            is_file = os.path.isfile(src)
            html = open(src, encoding="utf-8", errors="ignore").read() if is_file else None
            target = ("raw:" + html) if is_file else src
            cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=60000)
            try:
                r = await crawler.arun(url=target, config=cfg)
            except Exception as e:
                print(label, "crawl4ai error", e, file=sys.stderr)
                r = None
            if html is None:
                html = (r.html if r and r.html else "")
            d = analyze(label, src if not is_file else f"firecrawl rawHtml -> crawl4ai raw: ({os.path.basename(src)})", html, r)
            results.append(d)
            print(f"{label}: ok={d['crawl4ai_success']} words={d['word_count_markdown']} schema={d['jsonld_types']}", file=sys.stderr)
    json.dump(results, open(out, "w"), indent=1)


if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[args.index("--out") + 1]
    args = args[: args.index("--out")]
    asyncio.run(main(list(zip(args[::2], args[1::2])), out))
