"""Combine Texas (TDI open data) and Florida (DFS bulk files) license evidence into
one experience classification per agent. Usage:
  python combine.py <agents.xlsx> <tx_people.csv> <fl_matches.csv.gz> <out.pkl>"""
import re, sys, unicodedata
from collections import Counter, defaultdict
import pandas as pd

xlsx, txcsv, flgz, out = sys.argv[1:5]
TODAY = pd.Timestamp("2026-11-12")
SUFFIX = {"JR", "SR", "II", "III", "IV", "V"}

def toks(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"[.,'`\"()]", "", s).replace("-", " ")
    t = s.split()
    while len(t) > 2 and t[-1] in SUFFIX: t.pop()
    return t
def digits(p): return re.sub(r"\D", "", str(p))[-10:]
def yrs(d): return (TODAY - d).days / 365.25

ag = pd.read_excel(xlsx, sheet_name=0)

# ---------- Texas ----------
tx = pd.read_csv(txcsv, dtype=str)
tx["d"] = pd.to_datetime(tx["d"])
tx = tx.sort_values("d").drop_duplicates("npn")
freq = Counter(); tx_idx = defaultdict(list)
for r in tx.itertuples(index=False):
    t = toks(r.name)
    if len(t) < 2: continue
    freq[(t[0], t[-1])] += 1
    rec = (r.npn, r.name, r.state, r.d)
    keys = {(t[0], t[-1])} | ({(t[0], t[-2]), (t[0], t[1])} if len(t) >= 3 else set())
    for k in keys: tx_idx[k].append(rec)

# ---------- Florida ----------
fl = pd.read_csv(flgz, dtype=str, keep_default_na=False)
fl["d"] = pd.to_datetime(fl["License Issue Date"], errors="coerce")
fl["email"] = fl["Email Address"].str.strip().str.lower()
fl["phone"] = fl["Business Phone"].map(digits)
per = fl.groupby("NPN Number").agg(name=("Full Name", "first"), first=("First Name", "first"),
        last=("Last Name", "first"), res=("Residency Type", lambda s: "Resident" if (s == "Resident").any() else s.iloc[0]),
        st=("Business State", "first"), mst=("Mailing State", "first"), d=("d", "min"),
        email=("email", "first"), phone=("phone", "first"),
        types=("License TYCL Desc", lambda s: ", ".join(sorted(set(s))))).reset_index()
by_email = defaultdict(set); by_phone = defaultdict(set); by_name = defaultdict(set)
for r in per.itertuples(index=False):
    if r.email: by_email[r.email].add(r[0])
    if len(r.phone) == 10: by_phone[r.phone].add(r[0])
    ft, lt = toks(r.first), toks(r.last)
    if ft and lt:
        for l in {lt[-1], lt[0]}: by_name[(ft[0], l)].add(r[0])
per = per.set_index("NPN Number")

rows = []
for a in ag.itertuples(index=False):
    t = toks(a.Name); st = a.State; ev = []   # evidence: (date, source, conf, resident_state_source, note)
    # --- Florida ---
    email = str(a.Email).strip().lower() if isinstance(a.Email, str) else ""
    hit, how = set(), ""
    if email and email in by_email: hit, how = by_email[email], "email"
    elif digits(a.Phone) in by_phone and len(by_phone[digits(a.Phone)]) <= 2: hit, how = by_phone[digits(a.Phone)], "phone"
    if hit and len(t) >= 2:   # require name sanity for email/phone hits shared by several people
        named = {n for n in hit if t[0] in toks(per.at[n, "first"]) or t[-1] in toks(per.at[n, "last"])}
        hit = named or (hit if len(hit) == 1 else set())
    if not hit and len(t) >= 2:
        cands = set()
        for k in {(t[0], t[-1])} | ({(t[0], t[-2]), (t[0], t[1])} if len(t) >= 3 else set()):
            cands |= by_name.get(k, set())
        cands = {n for n in cands if st in (per.at[n, "st"], per.at[n, "mst"])}
        if len(cands) == 1: hit, how = cands, "name+state"
        elif len(cands) > 1: how = f"ambiguous ({len(cands)} same-name FL licensees in {st})"
    if len(hit) == 1:
        n = next(iter(hit)); p = per.loc[n]
        if pd.notna(p.d):
            resident = p.res == "Resident"
            if how in ("email", "phone"): conf = "High"
            elif st == "FL" and resident: conf = "High"
            else: conf = "Medium" if freq.get((t[0], t[-1]), 0) <= 2 else "Low"
            ev.append((p.d, f"FL DFS (NPN {n}, matched by {how})", conf, resident and st == "FL",
                       f"FL {'resident' if resident else 'non-resident'} license since {p.d.date()} ({p.types})"))
    fl_note = how if not hit else ""
    # --- Texas ---
    if len(t) >= 2:
        cands = {}
        for k in {(t[0], t[-1])} | ({(t[0], t[-2]), (t[0], t[1])} if len(t) >= 3 else set()):
            for c in tx_idx.get(k, []): cands[c[0]] = c
        ins = [c for c in cands.values() if c[2] == st]
        full = " ".join(t)
        if len(ins) > 1:
            ex = [c for c in ins if " ".join(toks(c[1])) == full]
            if len(ex) == 1: ins = ex
        npns_fl = {n for n in hit} if hit else set()
        if len(ins) == 1:
            c = ins[0]; legacy = c[3].year == 1920
            if c[0] in npns_fl: conf = "High"           # same NPN confirmed by Florida match
            elif st == "TX": conf = "High"
            else: conf = "Medium" if freq.get((t[0], t[-1]), 0) <= 2 else "Low"
            ev.append((pd.Timestamp("1990-01-01") if legacy else c[3], f"TX TDI (NPN {c[0]})", conf, st == "TX",
                       "TX legacy record (pre-electronic, exact year unknown)" if legacy else
                       f"TX {'resident' if st == 'TX' else 'non-resident'} license since {c[3].date()}"))
        elif len(ins) > 1 and st == "TX":
            ds = sorted(c[3] for c in ins)
            if yrs(ds[-1]) >= 1:
                ev.append((ds[-1], "TX TDI", "Medium", True, f"{len(ins)} same-name TX licensees, all licensed 1+ yrs; years = minimum"))
    # --- decide ---
    good = [e for e in ev if e[2] in ("High", "Medium")]
    cat, years, conf, src, note = "Not sure", None, "No record", "", ""
    if good:
        best = min(good, key=lambda e: e[0])
        y = yrs(best[0]); conf = "High" if any(e[2] == "High" for e in good) else "Medium"
        src = "; ".join(e[1] for e in good); note = " | ".join(e[4] for e in good)
        if y >= 1:
            cat, years = "More than a year", int(y)
            if "legacy" in best[4]: years = None
            if not any(e[3] for e in good): note += " | years are a minimum (home-state license may be older)"
        elif any(e[3] for e in good):
            cat = "Less than a year"
        else:
            note += " | only recent non-resident license(s) found; home-state history unknown"
    elif ev:
        conf = "Low"; src = "; ".join(e[1] for e in ev)
        note = "Common name, possible match only: " + " | ".join(e[4] for e in ev)
    else:
        note = "No license record found in TX or FL public data" + (f"; FL {fl_note}" if fl_note else "")
    rows.append({"Experience Category": cat, "Years of Experience": years, "Confidence": conf, "Source": src, "Notes": note})

res = pd.concat([ag[["Name", "Phone", "Email", "State"]].reset_index(drop=True), pd.DataFrame(rows)], axis=1)
res.to_pickle(out)
print(res["Experience Category"].value_counts().to_string())
print(pd.crosstab(res["Experience Category"], res.Confidence))
print(pd.crosstab(res.State.where(res.State.isin(["FL", "TX"]), "Other"), res["Experience Category"]))
print("FL email matches:", res.Source.str.contains("matched by email").sum(), "phone:", res.Source.str.contains("matched by phone").sum())
