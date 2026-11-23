"""Open-source Trustpilot review extraction (BeautifulSoup + json): parses the page's
embedded __NEXT_DATA__ JSON. Usage: python3 oss_trustpilot_extract.py <html> <out.json>"""
import json, sys
from bs4 import BeautifulSoup
s = BeautifulSoup(open(sys.argv[1], encoding="utf-8").read(), "html.parser")
data = json.loads(s.find("script", id="__NEXT_DATA__").string)
pp = data["props"]["pageProps"]
bu = pp.get("businessUnit", {})
revs = []
for r in pp.get("reviews", []):
    revs.append({
        "rating": r.get("rating"),
        "published": (r.get("dates") or {}).get("publishedDate"),
        "experienced": (r.get("dates") or {}).get("experiencedDate"),
        "title": r.get("title"),
        "text": r.get("text"),
        "verified_label": (r.get("labels") or {}).get("verification", {}).get("isVerified"),
        "source": (r.get("labels") or {}).get("verification", {}).get("reviewSourceName"),
        "owner_reply": bool(r.get("reply")),
        "owner_reply_date": (r.get("reply") or {}).get("publishedDate"),
    })
out = {"business": {"name": bu.get("displayName"), "trust_score": bu.get("trustScore"), "stars": bu.get("stars"),
                    "review_count": bu.get("numberOfReviews"), "claimed": bu.get("isClaimed"),
                    "categories": [c.get("name") for c in bu.get("categories", [])] if bu.get("categories") else None},
       "reviews": revs}
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out["business"]))
for r in revs: print(r["rating"], r["published"][:10] if r["published"] else None, "reply" if r["owner_reply"] else "-", r["source"], "|", (r["title"] or "")[:60])
