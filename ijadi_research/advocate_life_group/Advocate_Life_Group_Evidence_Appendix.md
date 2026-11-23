# Advocate Life Group: Evidence Appendix

**Prepared by:** Ijadi research team
**Research window:** 23 Nov 2026, 17:36–17:50 UTC (12:36–12:50 ET)
**Companion to:** `Advocate_Life_Group_Brief.pdf` / `.docx`

Confidence tags:
- **Verified:** observed directly in a primary source on the date shown.
- **Estimated:** a modelled or third-party number (keyword volumes, funnel math).
- **Inferred:** a reasonable conclusion from evidence that was not observed directly.

Search results and AI answers are personalized and change over time. Every SERP below records the location and timestamp it was pulled from. Local-pack and organic positions are snapshots, not guarantees.

---

## 0. Tools used, and what failed

| Tool | Status | What it did / what we used instead |
|---|---|---|
| **crawl4ai** (local repo, v0.8.x, this branch) | ⚠️ **Partially blocked, then worked around.** This cloud container's network policy refused outbound connections to `advocatelifegroup.com` and all competitor domains (HTTP 403 from the egress proxy). | Firecrawl fetched each page's **raw HTML** (`formats: rawHtml`). crawl4ai then parsed that HTML locally through its `raw:` input (`AsyncWebCrawler.arun("raw:<html>")`) plus a BeautifulSoup audit layer. Script: `scratchpad/c4a_audit.py` (copied to `evidence/c4a_audit.py`). Outputs: `crawl/client_home.json`, `crawl/client_posts.json`, `crawl/competitors.json`. A side effect: crawl4ai did not run a link-following deep crawl, so the page inventory comes from the XML sitemap instead (§1.2). |
| **Firecrawl** (MCP + Alexandria) | ✅ Used | Web search (localized), scraping, an agent job for the Ohio DOI license lookup, and Alexandria providers: `firecrawl-maps` (Google Maps listings, review trends), `dataforseo` (Google SERP + Google Ads keyword volume), `finra-org` (BrokerCheck), `bbb-org` (BBB search). |
| **Apify** | ❌ **Not available.** (Re-run with open-source tools: see §11.) The Composio Apify toolkit has **no connected account**. A connection link was generated (Composio account `apify_syne-pasan`, status "initiated") but never completed. | GBP/Maps data came from Alexandria `firecrawl-maps` (business search + `rating_trend` for review velocity and owner-response rate). SERP and People-Also-Ask data came from Alexandria `dataforseo/serp/google-organic`. Social profiles were checked through Firecrawl search. Facebook could not be scraped (Firecrawl: "site not supported"). |
| **Live AI assistants** (ChatGPT, Perplexity, Gemini, Copilot) | ❌ **Not tested.** No OpenAI, Perplexity or Gemini account is connected in Composio (checked 23 Nov 2026 17:44 UTC). | The GEO assessment uses proxies: (a) Google AI Overview presence and citations from DataForSEO SERPs, (b) the **retrieval set** a web-grounded assistant would draw on (Firecrawl search for the same prompts), and (c) presence on the directories those engines usually cite. Every GEO finding is therefore tagged **Inferred**. |
| **Ohio Secretary of State** | ❌ Not retrieved | `businesssearch.ohiosos.gov` served a bot security check to the Firecrawl agent. The legal entity name, filing date and registered agent are **Not found**. |
| **Mystery shop** | ⏸ Not run | Not approved by the user. All lead-handling findings are visual inspections of forms and funnels. No inquiry was submitted. |
| **PageSpeed Insights / Core Web Vitals** | ❌ Not run | PSI API not reachable from this container. Page weight was measured from the raw HTML instead (§1.3). |
| **Backlinks** (Serpstat / DataForSEO backlinks) | ⏸ Not run (budget) | Authority is listed as a **research gap**. Recommended for the Day 0–30 baseline. |

---

## 1. Website audit (crawl4ai on Firecrawl raw HTML)

### 1.1 robots / sitemap / llms.txt (Firecrawl scrape, `maxAge:0`, 23 Nov 2026 17:37 UTC)
| File | Result | Confidence |
|---|---|---|
| `/robots.txt` | 200. `Disallow: /wp-admin/`, `Crawl-delay: 10`, `Sitemap: https://advocatelifegroup.com/wp-sitemap.xml` | Verified |
| `/wp-sitemap.xml` | 200. WordPress core sitemap: posts, pages, category, my-calendar event categories | Verified |
| `/sitemap_index.xml` | **404** (no SEO plugin sitemap) | Verified |
| `/llms.txt` | **404** | Verified |
| 404 page weight | ~1.73 MB HTML | Verified |

### 1.2 Page inventory (from `wp-sitemap-posts-*.xml`)
- **Pages: 2.** `/` (lastmod 2026-06-10) and `/my-calendar/` (2023-03-08). Verified.
- **Posts: 99.** From 2025-04-28 to 2026-11-23. Since 20 May 2026 a post has been published **every ~2 days at ~02:40–05:30 UTC**. That cadence points to an automated content feed. Inferred (Verified: timestamps).
- **No standalone product, service or city pages.** The 12 services (Life Insurance, Mortgage Protection, LTC, etc.) are on-page anchors (`/#3652c841a7e7ac6ad`). Verified.
- URLs mentioning Ohio, Columbus, Mount Vernon or Knox: **0 of 101.** Verified.

### 1.3 Homepage (crawl4ai `raw:` parse, `crawl/client_home.json`)
| Signal | Finding | Confidence |
|---|---|---|
| Title | "Advocate Life Group – Retire Confidently" (40 chars); no "life insurance" or "Ohio" | Verified |
| Meta description | Auto-extracted body text with line breaks ("Retirement Planning \n ...") | Verified |
| og:title | Empty | Verified |
| H1s | **4** ("Retire Confidently.", "Advocate Life Group", "Our E-newsletter", "Contact Us") | Verified |
| JSON-LD schema | **None.** No microdata either | Verified |
| HTML weight | **1.94 MB**, of which **1.32 MB is inline CSS**; 179 `<script>` tags | Verified |
| Images | 40; **29 missing alt text** | Verified |
| Analytics | Legacy `ga.js` with `UA-3329706-1` only. Universal Analytics stopped processing data in July 2023. **No GA4 or GTM tag found.** | Verified (tag) / Inferred (no working analytics) |
| Generator / theme | WordPress + Avada/Fusion Builder; plugins: contact-form-7, cf7-submissions, my-calendar, wonderplugin; **no SEO plugin** | Verified |
| Phone | (617) 650-1578 only (a Massachusetts area code) | Verified |
| Address | "Mount Vernon, Ohio 43050" with **no street**; map link is bare `https://www.google.com/maps` | Verified |
| Map embed | Renders "Oops! Something went wrong. This page didn't load Google Maps correctly." | Verified (Firecrawl markdown) |
| Nav "Contact Us" (Have a Question? block) | Links to **`https://simplicity.my.salesforce.com/`**, a Salesforce login page and not a contact form | Verified |
| Team popups (rendered in HTML on every page) | "Rita Nelson – Office Manager", "Steve Markes – Financial Advisor", "April Drew – Wealth Management", "Athan Poullas – **Co-Founder**", each with **Lorem ipsum** bios (4 occurrences) | Verified |
| Founder block | "Athan Poullas, **Founder**", US Marine veteran from Columbus, Ohio; private and federal retirement markets | Verified |
| Terms of Use | Contains the placeholder "**Click here (insert link)** to see our Privacy Policy" | Verified |
| Privacy policy opt-out email | `mailto:contact@llonebeacon.com` displayed as "contact@lonebeacon.com" (another firm's address, misspelled) | Verified |
| Typos | "Stress Free **Retriement**"; "Increase you or your loved one's…" | Verified |
| Forms (CF7) | Newsletter (name, email); "Speak With…" and "Retirement Review" (name, email, phone, **Net Investable Assets\*: $100–250K / $250–500K / $500K–1M / $1M+**, How did you hear) | Verified |
| Consent language at form | **None at point of capture.** The privacy policy claims submission = permission to contact "through any means… text message" | Verified |
| Chat / booking widget | **None.** Keyword hits for intercom, hubspot and crisp were Font Awesome icon CSS and a WP shadow preset (false positives, checked manually) | Verified |
| Template provenance | Page author `kirby-macksimplicitygroup-com` (Simplicity Group); book offers *Stress-Free Retirement*, *Tax-Free Retirement*; CalcXML calculators | Verified (author slug) / Inferred (IMO-provided template) |
| Compliance-sensitive copy | "guaranteed lifetime income", "monitor and adjust **until the end of time**" | Verified |

### 1.4 Blog posts sampled (crawl4ai `raw:`; `crawl/client_posts.json`)
| URL | Article words | Author byline | Schema | Notes |
|---|---|---|---|---|
| /term-life-vs-whole-life-retirement-planning/ (2026-11-17) | 1,367 | none (empty vcard) | none | Balanced and well written; H2s are not phrased as questions; no FAQ block; no Ohio angle |
| /is-life-insurance-good-for-retirement/ (2026-08-15) | 1,392 | none | none | Opens with a direct answer ("it can be, but only when…"), which is strong AEO raw material |

---

## 2. Business facts (Phase 0)

| Fact | Finding | Source / tool / date | Confidence |
|---|---|---|---|
| Trade name | Advocate Life Group | advocatelifegroup.com (Firecrawl, 23 Nov 2026) | Verified |
| Legal entity | **Not found** (Ohio SOS blocked; ODI agency search returned none) | businesssearch.ohiosos.gov; ODI locator (Firecrawl agent) | Not found |
| Principal | Athan Poullas (ODI: **Athanasios G. Poullas**), NPN **18341865**, USMC veteran per site | Site; ODI locator | Verified |
| Ohio license | **Active: Non-Resident Major Lines #1763458** (Life; Accident & Health), issued **10 Aug 2026**, expires 31 Jan 2029. Ohio **resident** license #1660132 **surrendered 30 Jul 2026 ("Clearance Request")**. Resident state on record: **Virginia**. Phone of record (617) 650-1578 | ODI public agent locator via Firecrawl agent, 23 Nov 2026 17:47 UTC: https://gateway.insurance.ohio.gov/UI/ODI.Agent.Public.UI/AgentLocator.mvc/DisplayIndividualDetail/iL!2b3zGy0sI2mXMVjX1jAtA!3d!3d | Verified (third-party agent read the record; we recommend the owner confirm) |
| Other agents (brief assumed 3–4) | **None verifiable.** Only one "Poullas" record exists. Team names on the site sit beside Lorem-ipsum bios and look like template placeholders | Site; ODI | Inferred |
| Securities / IAR registration | **None found** for Athan Poullas on FINRA BrokerCheck | Alexandria `finra-org/brokercheck_search`, 23 Nov 2026 | Verified (absence) |
| Affiliation | Listed as "Licensed Strategist" at **Tax Free Wealth Plan LLC** (national; NPN 21442325; "appointed with 25 companies"; life insurance + annuities; "not an RIA") | https://www.taxfreewealthplan.com/about-us, /licensing (Firecrawl, 23 Nov 2026) | Verified |
| Marketing platform | Website built on a Simplicity Group template (author slug; Salesforce link `simplicity.my.salesforce.com`) | Site HTML | Inferred |
| Carriers | Not listed on the site. Via TFWP: "25 companies" (unnamed) | TFWP | Not found (specific carriers) |
| Product mix (evidence) | Retirement income planning, annuities (FIA, QLAC posts), **IUL** (2 Trustpilot reviews, IUL funnel), life (term/whole/IUL), LTC, mortgage protection, Medicare/health, Social Security | Site, Trustpilot, funnel | Verified (marketed) |
| Target segments | Pre-retirees/retirees with **$100K+ investable assets** (form gate); federal employees ("federal retirement markets"); veteran families (a Trustpilot review) | Site, Trustpilot | Verified/Inferred |
| Lead sources (visible) | (1) **Facebook-ad funnel** at `athanpoulla.info` (GoHighLevel / LeadConnector): "Get Pre-Qualified For A Cash Value I.U.L Policy" with a 30-min booking page carrying a Facebook disclaimer; (2) website forms; (3) workshop/webinar options in the "How did you hear" list; (4) referrals (Trustpilot) | Firecrawl scrape of https://athanpoulla.info/, 23 Nov 2026 | Verified (funnel exists) / Inferred (ads drive it) |
| Address used publicly | "301 Teryl Dr, Mount Vernon 43050" (Trustpilot); "Mount Vernon, Ohio 43050" (site, no street); ODI address of record is in Mechanicsville, VA | Trustpilot; site; ODI | Verified (conflict) |
| Email | info@advocatelifegroup.com (Trustpilot); athan@advocatelifegroup.com (site mailto) | Trustpilot; site | Verified |
| Social | Facebook page `facebook.com/p/Advocate-Life-Group-61581467277645/` ("veteran owned, **nationally recognized leader** in retirement and legacy planning"); Instagram posts (#RetirementPlanning; copy says "**fiduciary-first guidance**"); founder Instagram @athanpoullas (8 posts, 127 followers); LinkedIn directory lists "Athan Poullas, Mount Vernon, OH, Advocate Life Group" | Firecrawl search snippets, 23 Nov 2026 (Facebook not scrapeable) | Verified (snippets) |

### 2.1 NAP consistency
| Source | Name | Address | Phone |
|---|---|---|---|
| Website | Advocate Life Group | Mount Vernon, OH 43050 (no street) | (617) 650-1578 |
| Trustpilot | Advocate Life Group | 301 Teryl Dr, Mount Vernon 43050 | 6176501578 |
| Ohio DOI (producer record) | Athanasios G Poullas | Mechanicsville, VA | (617) 650-1578 |
| Google Business Profile | **Not found** | – | – |
| BBB | **Not found** (0 results, Mount Vernon OH) | – | – |
| Yelp / Yellow Pages (Mount Vernon life insurance lists) | **Not listed** | – | – |
| Facebook | Advocate Life Group | not visible in snippet | not visible |

---

## 3. Reputation

**Trustpilot** (https://www.trustpilot.com/review/advocatelifegroup.com, Firecrawl, 23 Nov 2026). Verified.
- TrustScore **4.4 / 10 reviews**, all 10 in the last 12 months, all rated 5★. Claimed Dec 2025. Trustpilot note: "No recent history of asking for reviews."
- Owner replies: 3 of 10, all on 13 Jan 2026; **none since**.
- Review themes (our coding of the 10 texts):
  - Patience and clear explanations (5)
  - Follows through and responds quickly (4)
  - IUL restructuring or setup (2)
  - Switching from big firms (Merrill, a former "group/advisor-company") (3)
  - Veteran-benefits help and an in-home visit "7 years ago" (1)
  - "Not in it for the money" (2)
- Quotes (verbatim):
  - "He came to our home with valuable information about veterans benefits, (as my husband is a USMC disabled veteran)…" (19 Jun 2026)
  - "I had my iul policy structured wrong… Now Athan has my policy structure correctly…" (23 Jul 2026)
  - "Very timely and gets back to you quickly." (13 Jan 2026)

**Google reviews:** none, because no listing was found (firecrawl-maps name search, Mount Vernon and nationwide; the only "Advocate…" match was Advocate Insurance Group, Martinsburg WV). Verified (absence).

**Competitor review velocity:** see `evidence/competitor_review_velocity.json` and §5.

---

## 4. Search visibility (SEO / AEO)

### 4.1 Keyword demand: Ohio, Google Ads average monthly searches, Nov 2025–Oct 2026
Tool: Alexandria `dataforseo/keywords/search-volume`, location "Ohio, United States", pulled 23 Nov 2026 17:41 UTC. Full table: `evidence/keyword_volumes_ohio_dataforseo.csv`. **Estimated.**
Highlights: term vs whole life insurance 720 · iul insurance 390 + indexed universal life 260 · **fers retirement planning 390** · mortgage protection insurance 480 · life insurance near me 480 · life insurance agent near me 260 · how much life insurance do I need 260 · life insurance ohio 170 · veterans life insurance 110 · long term care insurance ohio 110 · retirement planner near me 90. City-level queries ("life insurance mount vernon ohio", "annuities columbus ohio") returned **no data** (too small for Google Ads).

### 4.2 Live Google SERPs: DataForSEO `serp/google-organic`, depth 20, desktop, 23 Nov 2026 17:42 UTC
Raw: `evidence/serp_dataforseo_batch1.json`; summary: `evidence/serp_summary_batch1.txt`.
Caveat: DataForSEO returned organic URLs as Google redirect tokens, so organic **domains** could not be confirmed from this tool. Local-pack, People Also Ask and AI Overview elements were usable. Organic presence was cross-checked with Firecrawl search (§4.3).

| Query (location) | AI Overview | Local pack (in order) | People Also Ask present | Client present |
|---|---|---|---|---|
| life insurance agent near me (Mount Vernon, OH) | Yes | Madison Collins Stephens 5.0 (127) · Kari Ball 4.8 (57) · Dumbaugh 5.0 (156) | Yes | **No** |
| life insurance mount vernon ohio (Mount Vernon) | Yes | Western & Southern 4.4 (9) · Madison Collins Stephens · Dumbaugh. Ads: Ladder, AARP, State Farm | Yes | **No** |
| life insurance columbus ohio (Columbus) | Yes | Association of Ohio Life Insurance 5.0 (5) · Brown Insurance 5.0 (65) · Grange 4.4 (1,600) | Yes | **No** |
| fers retirement planning ohio (Columbus) | Yes | Federal Employee Benefit & Retirement Agency 4.9 (897) · OPERS 3.2 (146) · Peak Retirement 5.0 (453) | Yes ("How do I calculate my FERS retirement benefits?") | **No** |
| annuity advisor columbus ohio (Columbus) | Yes | ANTOLINO Wealth 5.0 (91) · Peak Retirement · Johnson Investment Counsel | Yes | **No** |
| term vs whole life insurance (Columbus) | Yes. Cites fidelity.com, guardianlife.com, nerdwallet.com, protective.com, trustage.com, youtube.com | – | Yes ("Can you convert term to whole life?", "Does Dave Ramsey recommend…") | **No** |
| advocate life group (Columbus) | Yes (async, no text captured) | – | Yes | See §4.3 |
| retirement planning mount vernon ohio; iul agent columbus ohio; life insurance for veterans ohio | – | – | – | **Provider error (HTTP 502)**, not re-run |

Featured snippets owned by the client: **none observed.** PAA answers citing the client: **none observed.** Verified for the queries above only.

### 4.3 Organic cross-check: Firecrawl search (localized), 23 Nov 2026 17:43–17:45 UTC
| Query | Location | Client rank (top 20) | Who ranks |
|---|---|---|---|
| advocate life group | Columbus, OH | **#1** (advocatelifegroup.com); #3 Facebook page | Name collisions: Advocate Insurance Group (WV, IL), Wealth Advocate Group (OH), Advocate Health |
| life insurance agent Mount Vernon Ohio | Mount Vernon, OH | **Not in top 20** | Yelp, Griffin, Cunningham, Western & Southern, Jobes, Liberty Mutual locator, Yellow Pages, Madison Collins Stephens, Kahrl, BBB category, Nationwide locator, **DePolo life page**, State Farm, Dumbaugh |
| best life insurance agency in Mount Vernon Ohio | Mount Vernon, OH | **Not in top 15** | Cunningham, Griffin, Kahrl, AARP ad, Yelp, Jobes, Dumbaugh, Mployer, State Farm, Optimum (Facebook), Yellow Pages, Nationwide, Parker, Liberty Mutual, W&S |
| IUL indexed universal life agent Columbus Ohio | Columbus, OH | **Not in top 20** | Carriers (Nationwide, Columbus Life, Pacific Life), NerdWallet, a "Columbus Life IUL Fraud Lawsuit" page, Bankers Life, Horizon, SafeHarbor |
| veteran owned life insurance and retirement planning agent Ohio IUL annuity | Columbus, OH | **Not in top 15** | W&S, VA.gov, National Life, Ohio DOI guide, GEBA (feds & military), NY Life, CNBC, a Facebook group post asking for "a local annuity/IUL insurance agent… Northwest Ohio" |
| Is Advocate Life Group legit? reviews Athan Poullas | (US) | Trustpilot **#1**, website **#2** | – |

---

## 5. Competitors (Phase 4)

Selection: the local packs and organic results observed in §4, plus one national online seller seen in paid results. Google data: Alexandria `firecrawl-maps/businesses/search` (23 Nov 2026 17:40 UTC) and `rating_trend` (17:44 UTC). Site data: Firecrawl rawHtml parsed by crawl4ai (`crawl/competitors.json`, 17:44 UTC).

| Competitor | Type | Google rating (reviews) | Reviews last 12 mo | Owner reply rate | Local pack hits (of 5 tested packs) | Site schema (JSON-LD) | Booking/chat in page source | Differentiator |
|---|---|---|---|---|---|---|---|---|
| Madison Collins Stephens Agency, Mount Vernon & Newark (mcsinsurance.com) | Local independent (multi-line) | 5.0 (127) | 30 | 67% | 2 | Organization, WebSite | none | Two offices; call and text numbers |
| Dumbaugh Insurance, Mount Vernon (dumbaughinsurance.com) | Local independent | 5.0 (156) | 13 | 55% | 2 | InsuranceAgency, Organization | none | "Ohio's Premier Independent Insurance Agency" page |
| DePolo & Associates (Allstate), Mount Vernon (depoloinsurance.com/insurance/life) | Captive | 4.6 (190) | 30 | 97% | 0 | **FAQPage, Service**, Organization | none | Dedicated "Life & Retirement… Knox County families" page with FAQ schema |
| Tim Workman, State Farm, Mount Vernon (timworkmanagency.com) | Captive | 4.9 (352) | 40 | 98% | 0 | InsuranceAgency, **Person**, Service | **Calendly** | Brand plus review volume |
| Western & Southern Life, Mount Vernon office | Captive (life-focused) | 4.4 (9) | 1 | 44% | 1 | InsuranceAgency | **Calendly** | Only life-focused office in town |
| Peak Retirement Planning, Columbus (peakretirementplanning.com) | Retirement/annuity planner | 5.0 (453) | 60 in Oct–Nov 2026 | 97% | 2 (Columbus) | LocalBusiness, Organization | none | Active review campaign; "Midwestern Millionaires" niche |
| Ladder (ladderlife.com) | National online seller | n/a | n/a | n/a | Paid ad on "life insurance mount vernon ohio" | none | **Zendesk chat** | Instant online term quotes |
| **Advocate Life Group** | Independent (1 verified producer) | **No listing** | 0 (Google) / 10 (Trustpilot) | 30% (Trustpilot) | **0** | **none** | none on site; GHL booking on the ad funnel | USMC veteran founder; federal and private retirement; IUL reviews |

Checks for chat/booking false positives: crawl4ai keyword hits for "crisp", "drift" and "tidio" were CSS or YouTube tokens and were discarded. Zendesk (Ladder) and Calendly (W&S, State Farm) were confirmed by signature strings (`zendesk-widget-launcher`, `calendly.com` / `calendly_embed`).

---

## 6. GEO (AI assistants): log and proxies

**Live assistants tested: none** (see §0). Date of attempt: 23 Nov 2026. Prompt set prepared for the Day-0 baseline, to run in ChatGPT, Perplexity, Gemini, Google AI Overviews and Copilot from a Columbus-area IP, logged monthly:
1. Best life insurance agency in Mount Vernon, Ohio
2. Independent life insurance agent near Columbus, Ohio
3. Who can help me get term life insurance in Knox County, Ohio?
4. Recommend a final expense insurance agent in Ohio
5. Is Advocate Life Group legit? / What do you know about Advocate Life Group?
6. Who helps federal employees in Ohio plan FERS retirement income?
7. Veteran-owned life insurance or retirement planner in Ohio
8. Can someone review my IUL policy in Ohio?

**Proxy findings (Inferred):**
- Google AI Overviews appeared on **7 of 7** SERPs that returned data. The only one with captured citations ("term vs whole life insurance") cited national publishers and carriers. No local agency was cited.
- For local prompts (1–3), the retrieval set is Yelp, Yellow Pages, BBB category pages, carrier agent locators (State Farm, Nationwide, Liberty Mutual, Progressive) and local agency sites. **The client is in none of them**, so a web-grounded assistant has nothing to cite for it.
- For prompt 5, retrieval returns Trustpilot #1 and the website #2. An assistant would likely describe a 4.4-rated Trustpilot profile and a "veteran founder", and could repeat conflicting site facts: Founder vs Co-Founder, "Financial Advisor"/"Wealth Management" team members with placeholder bios, and a Massachusetts phone number. **Accuracy risk.**
- Entity signals: no `Organization`/`InsuranceAgency`/`Person` schema, no `sameAs` links, no `llms.txt`, and the name collides with several "Advocate…" firms.

---

## 7. Opportunity model: inputs and assumptions

Script: `evidence/opportunity_model.py`; output: `evidence/opportunity_model_output.json`. All values **Estimated**.

**Being found (month-12 run-rate, after ~6 months of build)**
- Priority-query demand: **~3,080 searches/month in Ohio.** That is the sum of the DataForSEO volumes listed in the script. "Near me" volume is multiplied by 0.19 (assumed share inside a reachable service area); "whole life insurance" and "roth conversion" are excluded as too broad.

| Scenario | Click share | Visit→inquiry | Qualified | Appt kept | Close | Avg first-year commission/case | Policies/yr | FYC/yr |
|---|---|---|---|---|---|---|---|---|
| Low | 1.0% | 1.0% | 50% | 50% | 25% | $2,500 | 0.2 | ~$600 |
| Base | 2.5% | 2.0% | 60% | 60% | 30% | $3,500 | 2.0 | ~$7,000 |
| High | 5.0% | 3.0% | 70% | 70% | 35% | $5,000 | 9.5 | ~$47,600 |

**Handling leads well (no new traffic)**
- Monthly inbound leads (owner to confirm): 20 / 40 / 60.
- Contact rate today 40% (assumption, paid-social leads with no instant follow-up), improving to 50% / 55% / 60%.
- Appointment-set rate of contacted: 40% (held constant).
- Show rate 60%, improving to 70% / 75% / 75% (reminders plus available slots).
- Close 30%; FYC/case as above.

| Scenario | Policies/yr today | After | Uplift | FYC uplift/yr |
|---|---|---|---|---|
| Low | 6.9 | 10.1 | +3.2 | ~$7,900 |
| Base | 13.8 | 23.8 | +9.9 | ~$34,800 |
| High | 20.7 | 38.9 | +18.1 | ~$90,700 |

**Commission references (third-party, not carrier schedules; owner's contracts govern):**
- IUL first-year commission ~80–110% of target premium; renewals 2–5% (https://unlockedcrm.ai/blog/iul-commission-structure-2026).
- FIA 3–7% of premium (https://unlockedcrm.ai/blog/insurance-commission-structures-explained; https://annuityjournal.org/annuities/annuity-commissions-explained/).
- Life first-year ranges by product (https://insuranceproagencies.com/insurance-agent-commission-structures).

**Speed-to-lead benchmarks (cross-industry, not insurance-specific, and dated):**
- HBR, "The Short Life of Online Sales Leads" (Oldroyd, McElheran, Elkington, Mar 2011): firms that contacted leads within an hour were ~7× more likely to qualify them than firms that waited longer; the study audited 2,241 US companies. https://hbr.org/2011/03/the-short-life-of-online-sales-leads
- InsideSales.com/MIT Lead Response Management Study (2007): calling within 5 vs 30 minutes gave ~100× contact odds and ~21× qualification odds. https://www.onecavo.com/wp-content/uploads/2015/11/MIT-InsideSales.com_Lead-Response-Management.pdf

**Market-size references:**
- Federal government employees, Columbus MSA: 15.3K (2024), FRED series SMU39181409091000001A. https://fred.stlouisfed.org/series/SMU39181409091000001A
- Knox County residents 65+: ~12,900 (20.3%, 2024). https://usafacts.org/answers/how-many-people-live-in-the-us/county/knox-county-oh/

---

## 8. Lead-handling inspection (Phase 5, visual only, no inquiry submitted)

| Path | Observation | Confidence |
|---|---|---|
| Website phone | (617) 650-1578 click-to-call; answer behaviour not tested | Verified (link) |
| Website "Contact Us" (Have a Question?) | Opens a **Salesforce login** (simplicity.my.salesforce.com) | Verified |
| Website forms | CF7 + reCAPTCHA. "Net Investable Assets" is required and starts at $100–250K, so it **screens out typical life/mortgage-protection buyers** | Verified |
| After submit | Confirmation, autoresponder or nurture: **not observable without submitting**. The cf7-submissions plugin stores entries in WordPress; no CRM integration was seen in the page source | Inferred |
| Ad funnel (athanpoulla.info, GoHighLevel) | "Thank you, your home qualifies! Step two: Schedule your appointment" (copy from a home-improvement template). Calendar: "**No slot available this month**" (viewed 23 Nov 2026). SMS consent: "you agree to receive text messages from **ALR Remodeling**… Text HELP to +1 818-200-8184" | Verified |
| Chat / text-us | None on the website | Verified |
| Analytics / attribution | Legacy UA tag only; no GA4/GTM; no call tracking seen | Verified (tags) |

---

## 9. Compliance references (not legal advice; for owner/counsel review)

- **Ohio Adm. Code 3901-6-01** (Solicitation of life insurance and/or annuity contracts). Among other provisions: advertising material must make clear when the product is life insurance (para. E). Sales presentations may not avoid "a clear and unequivocal statement that life insurance is the subject matter of the solicitation" (para. 26). Sales may only be made as a fully licensed life agent (para. 34). https://codes.ohio.gov/ohio-administrative-code/rule-3901-6-01 (Firecrawl, 23 Nov 2026). Verified.
- Copy to review: "guaranteed lifetime income" (guarantees depend on the issuing insurer's claims-paying ability), "nationally recognized leader" (Facebook; unsubstantiated), "**fiduciary-first**" (Instagram; no IAR/RIA registration found on BrokerCheck), "Financial Advisor"/"Wealth Management" placeholder titles, and "best" phrasing in post slugs (`/best-guaranteed-income-options/`, `/best-retirement-planning-companies/`).
- **TCPA:** the FCC's 2023 one-to-one consent rule was vacated by the 11th Circuit (*Insurance Marketing Coalition v. FCC*, Jan 24 2025) and later formally removed. Prior express **written** consent is still required for autodialed or prerecorded telemarketing calls and texts. https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/eleventh-circuit-vacates-tcpa-11-consent-rule · https://www.consumerfinanceinsights.com/2025/09/15/the-fcc-issues-final-rule-formally-eliminating-the-one-to-one-consent-requirement/
- **A2P 10DLC:** business texting from a local number requires brand and campaign registration in the business's own legal name. The current funnel's consent names a different business. Inferred risk.
- **Non-resident licensing:** advertising an Ohio "home" office while the producer's resident state is Virginia should be reviewed against Ohio's non-resident rules and Google Business Profile eligibility (a GBP requires a staffed, in-person location or a service-area business with a real address).

---

## 10. Research gaps
1. Live AI-assistant answers (ChatGPT, Perplexity, Gemini, Copilot): not tested.
2. Apify (GBP Q&A, photos, posts, social scraping): not connected.
3. Ohio SOS entity record: blocked.
4. Backlinks and referring domains: not pulled.
5. Core Web Vitals / PageSpeed: not run (only page weight measured).
6. Actual lead volume, contact rate, show rate and commissions: need the owner's numbers (the model uses stated placeholders).
7. Agent roster: only one producer verified. Need the names of any other agents to check ODI.
8. Three SERP calls returned provider errors (§4.2) and were not re-run.

---

## 11. Open-source re-run of the GBP and review scraping (23 Nov 2026, 17:57–18:01 UTC)

**Why:** Apify was not connected. This re-run replaces the hosted Maps provider with open-source scraping code.

**How:**
- **Fetch:** this container's egress policy blocks google.com, trustpilot.com and the other review sites (HTTP 403). The public pages were therefore fetched as rendered HTML by Firecrawl (`rawHtml`, `waitFor` 5–9 s, US location).
- **Parse (open source):** [`evidence/oss_gbp_extract.py`](evidence/oss_gbp_extract.py) uses crawl4ai's `JsonCssExtractionStrategy` on `raw:` HTML for the Maps result cards, and BeautifulSoup for profile panels (rating, star histogram, address, phone, website, booking link, hours, owner updates, the top 3 visible reviews and owner replies). [`evidence/oss_trustpilot_extract.py`](evidence/oss_trustpilot_extract.py) parses Trustpilot's embedded `__NEXT_DATA__` JSON.
- **Outputs:** `evidence/oss_gbp_search.json`, `evidence/oss_gbp_places.json`, `evidence/oss_trustpilot_reviews.json`. Raw HTML is in `raw/gbp/` (git-ignored).
- **Not used:** an attempt to call Google's internal review-list endpoint (`listentitiesreviews`, used by some open-source review scrapers) was refused by this session's permission policy. Only public, user-facing pages were used.
- **Limits:** without clicking and scrolling, a profile page shows only the 3 "most relevant" reviews. Full 12-month review velocity therefore still comes from the earlier `firecrawl-maps/rating_trend` pull (§3, §5). Running an open-source scraper such as `gosom/google-maps-scraper` locally, on a machine with open network access, would collect full review lists.

### 11.1 Google Maps searches (rank = order in the Maps result list)
| Search | Places | Advocate Life Group listed? | Top 5 |
|---|---|---|---|
| Advocate Life Group Mount Vernon OH | 14 | **No** | Mount Vernon Financial – (0); Giles Law Group 4.0 (51); Griffin Insurance 4.5 (71); Moore Law Firm 5.0 (22); Cooper, Adel, Vu & Associates, LPA - Centerburg 4.8 (243) |
| Advocate Life Group | 17 | **No** | Loss of Life Advocates 5.0 (3); Kiki Aguero Advocacy Group Inc 5.0 (8); LegalEASE, A LEGAL ACCESS Company 4.8 (1642); Advocates Real Estate Group at KWSW - Bincy Jacob Realtor & Team 5.0 (106); The de la Garza Law Group 4.9 (221) |
| life insurance agency Mount Vernon OH | 27 | **No** | Jobes Insurance Agency 4.9 (157); Griffin Insurance 4.5 (71); Kari Ball Insurance Agency 4.8 (57); Parker Agency LLC 5.0 (36); Optimum Insurance LLC 5.0 (51) |
| retirement planning Mount Vernon OH | 15 | **No** | Mount Vernon Financial – (0); Spearman Financial Services LLC 5.0 (13); Mosaic Financial Group LLC 3.0 (2); Lambert Investment Group – (0); Edward Jones - Financial Advisor: Sara A Mankins, CEPA®|RICP® 5.0 (4) |
| life insurance agency Columbus OH | 40 | **No** | Globe Life Liberty National Division: The Kafkis Agencies 4.8 (162); Auto and Home Insurance in Columbus Ohio \| Slyman Insurance Group Ohio 5.0 (437); Solid Insurance 4.6 (315); The Life Insurance Empire 5.0 (42); Globe Life American Income Division: Surace Smith & Partners Organization 4.9 (2017) |
| FERS federal retirement planning Columbus OH | 14 | **No** | Peak Retirement Planning, Inc. 5.0 (453); OPERS 3.2 (146); Frazier Financial Advisors, LLC 4.9 (31); Retirement Plans, Inc. 5.0 (1); Federal Employee Benefit & Retirement Agency 4.9 (897) |
| annuity advisor Columbus OH | 40 | **No** | Frazier Financial Advisors, LLC 4.9 (31); Libertas Wealth Management Group 5.0 (64); rebel Financial 5.0 (94); ANTOLINO Wealth Advisors 5.0 (91); Ross Wealth Advisors 4.6 (34) |

Result: **no Google Business Profile for Advocate Life Group in any of the 7 searches**, including an exact-name search with no location (Verified, absence). Name collisions in that search: Advocate Insurance Group (WV), Advocate Financial, Advocate Investing Services (MD), Loss of Life Advocates.

### 11.2 Competitor profiles (public place pages)
| Profile | Category | Rating | Reviews (histogram total) | 1–3★ | Address shown | Booking link | Owner updates | Top-3 reviews with owner reply | Newest of top 3 |
|---|---|---|---|---|---|---|---|---|---|
| Dumbaugh Insurance | Insurance agency | 5.0 | 156 | 1 | 122 S Main St, Mt Vernon, OH 43050 | calendly.com | Yes | 2 of 3 | 6 months ago, 9 months ago, 8 months ago |
| Federal Employee Benefit & Retirement Agency | Financial planner | 4.9 | 897 | 8 | **none (service-area)** | calendly.com | No | 0 of 3 | 5 months ago, 4 months ago, 5 months ago |
| Madison Collins Stephens Agency | Insurance agency | 5.0 | 127 | 0 | 214 E Chestnut St, Mt Vernon, OH 43050 | – | No | 0 of 3 | a week ago, 4 months ago, 5 months ago |
| Tim Workman - State Farm Insurance Agent | Insurance agency | 4.9 | 352 | 11 | 1590 Coshocton Ave Unit A, Mt Vernon, OH 43050 | timworkmanagency.com | Yes | 3 of 3 | a month ago, 3 weeks ago, 4 months ago |
| Peak Retirement Planning, Inc. | Financial advisor | 5.0 | 453 | 3 | Bldg 501, 3600 Olentangy River Rd, Columbus, OH 43214 | – | No | 3 of 3 | a week ago, a week ago, 2 weeks ago |
| DePolo & Associates, Inc.: Allstate Insurance | Insurance agency | 4.6 | 190 | 21 | 502 Coshocton Ave, Mt Vernon, OH 43050 | allstate.com | Yes | 1 of 3 | 3 weeks ago, 2 weeks ago, 2 months ago |
| Western & Southern Life | Life insurance agency | 4.4 | 9 | 1 | 1650 Coshocton Ave A, Mt Vernon, OH 43050 | – | No | 2 of 3 | 6 years ago, 7 years ago, 9 years ago |

Finding: **FEBRA**, the federal-retirement specialist ranking #5 for the Columbus FERS search, shows **no public address** (service-area listing), uses a Calendly booking link and runs phone appointments. It is a working model for a practice without an Ohio storefront. (Verified, observation; eligibility for the client still depends on a real verifiable address.)

### 11.3 Client reviews: Trustpilot (open-source parse)
- Advocate Life Group: TrustScore 4.4, 10 reviews, claimed: True, categories: Life Insurance Agency, Non-Bank Financial Service.
- Every review is 5★ and labelled "Organic" (unprompted). Publish dates: 2026-08-12, 2026-07-23, 2026-07-16, 2026-06-19, 2026-06-18, 2026-04-16, 2026-04-10, 2026-01-13, 2025-12-31, 2025-12-31.
- Owner replies: 3 of 10 (all dated 2026-01-13). **No new review since 2026-08-12** (about 3.5 months). Verified.
