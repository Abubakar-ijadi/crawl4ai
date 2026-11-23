"""Conservative opportunity model for Advocate Life Group.

Every input is either sourced (see Evidence Appendix, section 7) or a labeled assumption.
Run: python3 opportunity_model.py  -> prints tables and writes opportunity_model_output.json
"""
import json

# ---------- A. BEING FOUND -------------------------------------------------
# Source: DataForSEO keywords/search-volume (Google Ads), location=Ohio, avg monthly
# searches Nov-2025..Oct-2026, pulled 2026-11-23. Duplicate keyword pairs that Google Ads
# reports with identical metrics are counted once.
PRIORITY_QUERIES = {
    "iul insurance + indexed universal life insurance": 390 + 260,
    "fers retirement planning": 390,
    "veterans life insurance / life insurance for veterans (same metrics, counted once)": 110,
    "long term care insurance ohio": 110,
    "term vs whole life insurance": 720,
    "how much life insurance do i need": 260,
    "fixed indexed annuity": 50,
    "mortgage protection insurance": 480,
    "life insurance ohio": 170,
    # Local 'near me' (480 + 260 Ohio-wide). Assumption: only ~19% is within a
    # reachable service area (Columbus MSA share of Ohio population, rounded).
    "life insurance near me + life insurance agent near me (x0.19 service-area share)": round((480 + 260) * 0.19),
}
MONTHLY_DEMAND = sum(PRIORITY_QUERIES.values())

FOUND = {  # month-12 run-rate assumptions (after ~6 months of build)
    "low":  {"ctr": 0.010, "inquiry": 0.010, "qualified": 0.50, "appt_kept": 0.50, "close": 0.25, "fyc": 2500},
    "base": {"ctr": 0.025, "inquiry": 0.020, "qualified": 0.60, "appt_kept": 0.60, "close": 0.30, "fyc": 3500},
    "high": {"ctr": 0.050, "inquiry": 0.030, "qualified": 0.70, "appt_kept": 0.70, "close": 0.35, "fyc": 5000},
}

# ---------- B. HANDLING LEADS WELL (no new traffic) --------------------------
# Owner must confirm lead volume; these are placeholders based on visible paid-social funnel.
LEADS = {
    "low":  {"leads": 20, "contact_now": 0.40, "contact_new": 0.50, "set": 0.40, "show_now": 0.60, "show_new": 0.70, "close": 0.30, "fyc": 2500},
    "base": {"leads": 40, "contact_now": 0.40, "contact_new": 0.55, "set": 0.40, "show_now": 0.60, "show_new": 0.75, "close": 0.30, "fyc": 3500},
    "high": {"leads": 60, "contact_now": 0.40, "contact_new": 0.60, "set": 0.40, "show_now": 0.60, "show_new": 0.75, "close": 0.30, "fyc": 5000},
}


def found(s):
    a = FOUND[s]
    clicks = MONTHLY_DEMAND * a["ctr"] * 12
    inq = clicks * a["inquiry"]
    q = inq * a["qualified"]
    appts = q * a["appt_kept"]
    pol = appts * a["close"]
    return dict(clicks_yr=clicks, inquiries_yr=inq, qualified_yr=q, appts_yr=appts, policies_yr=pol, fyc_yr=pol * a["fyc"])


def handled(s):
    a = LEADS[s]
    def run(contact, show):
        c = a["leads"] * contact
        st = c * a["set"]
        sh = st * show
        return sh * a["close"]
    now = run(a["contact_now"], a["show_now"]) * 12
    new = run(a["contact_new"], a["show_new"]) * 12
    return dict(policies_now_yr=now, policies_new_yr=new, uplift_policies_yr=new - now, uplift_fyc_yr=(new - now) * a["fyc"])


if __name__ == "__main__":
    out = {"monthly_demand_ohio": MONTHLY_DEMAND, "queries": PRIORITY_QUERIES,
           "found": {s: found(s) for s in FOUND}, "handled": {s: handled(s) for s in LEADS},
           "assumptions": {"found": FOUND, "handled": LEADS}}
    print("Monthly priority-query demand (Ohio):", MONTHLY_DEMAND)
    for s in FOUND:
        f = found(s); h = handled(s)
        print(f"{s:5} FOUND: clicks/yr {f['clicks_yr']:.0f} inq {f['inquiries_yr']:.1f} qual {f['qualified_yr']:.1f} appts {f['appts_yr']:.1f} pol {f['policies_yr']:.1f} FYC ${f['fyc_yr']:,.0f}")
        print(f"      HANDLED: pol now {h['policies_now_yr']:.1f} -> {h['policies_new_yr']:.1f} (+{h['uplift_policies_yr']:.1f}) FYC +${h['uplift_fyc_yr']:,.0f}")
    json.dump(out, open(__file__.replace(".py", "_output.json"), "w"), indent=1)
