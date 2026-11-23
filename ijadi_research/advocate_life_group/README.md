# Advocate Life Group: Ijadi growth brief (23 Nov 2026)

| File | What it is |
|---|---|
| `Advocate_Life_Group_Brief.pdf` / `.docx` | The 3-page owner brief (same content; DOCX generated from `build/brief.html`) |
| `Advocate_Life_Group_Evidence_Appendix.md` | Every source, tool, date, confidence tag, SERP/AI log and assumption |
| `crawl/*.json` | crawl4ai page audits (client homepage, 2 posts, 7 competitor pages) |
| `evidence/` | SERP, Maps/BrokerCheck, keyword volume, review velocity, ODI licensing, opportunity model (`python3 evidence/opportunity_model.py`) |
| `build/` | `brief.html` (PDF source), `html_to_docx.py` (DOCX generator) |

Rebuild:
- PDF: render `build/brief.html` with Chromium/Playwright (`page.pdf({format:'Letter', preferCSSPageSize:true, printBackground:true})`).
- DOCX: `python3 build/html_to_docx.py build/brief.html Advocate_Life_Group_Brief.docx`.

`raw/` (third-party HTML fetched via Firecrawl) is git-ignored; re-fetch with Firecrawl `rawHtml` and pass to `evidence/c4a_audit.py`.
