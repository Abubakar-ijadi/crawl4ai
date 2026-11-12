"""Build 'more than 1 year of experience' contact lists from the full Florida DFS and
Texas TDI licensee data. Usage: python export_contacts.py <fl_links.json> <outdir>"""
import csv, glob, io, json, os, re, sys, time, zipfile
import pandas as pd, requests
links_file, outdir = sys.argv[1:3]
os.makedirs(outdir, exist_ok=True)
TODAY = pd.Timestamp.today().normalize()
UA = {"User-Agent": "Mozilla/5.0"}
def yrs(d): return ((TODAY - d).dt.days / 365.25)

# ---------------- Florida ----------------
links = [l for l in json.load(open(links_file)) if "AllValidLicensesIndividual" in l]
parts = []
for url in links:
    print("FL download", url, flush=True)
    r = requests.get(url, timeout=900, headers=UA); r.raise_for_status()
    parts.append(pd.read_csv(io.BytesIO(r.content), dtype=str, keep_default_na=False))
fl = pd.concat(parts, ignore_index=True); del parts
print("FL license rows", len(fl), flush=True)
for c in fl.columns:   # FL wraps some values as Excel formulas, e.g. ="537097"
    fl[c] = fl[c].str.replace(r'^="(.*)"$', r"\1", regex=True).str.strip()
fl["d"] = pd.to_datetime(fl["License Issue Date"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
fl = fl[fl["NPN Number"].str.strip() != ""]
fl = fl.sort_values("d")
first = "first"   # pandas 'first' = first non-null value per group
CC = ["Email Address", "Business Phone", "Business Address1", "Business Address2", "Business City",
      "Business State", "Business Zip", "Business County", "Mailing Address", "Mailing City",
      "Mailing State", "Mailing Zip"]
fl[CC] = fl[CC].replace("", pd.NA)
fl["is_res"] = fl["Residency Type"] == "Resident"
agg = fl.groupby("NPN Number").agg(**{
    "Full Name": ("Full Name", "first"), "First Name": ("First Name", "first"),
    "Middle Name": ("Middle Name", "first"), "Last Name": ("Last Name", "first"),
    "Email": ("Email Address", first), "Business Phone": ("Business Phone", first),
    "Business Address": ("Business Address1", first), "Business Address 2": ("Business Address2", first),
    "Business City": ("Business City", first), "Business State": ("Business State", first),
    "Business Zip": ("Business Zip", first), "Business County": ("Business County", first),
    "Mailing Address": ("Mailing Address", first), "Mailing City": ("Mailing City", first),
    "Mailing State": ("Mailing State", first), "Mailing Zip": ("Mailing Zip", first),
    "Residency": ("is_res", "any"),
    "Earliest License Issue Date": ("d", "min"),
}).reset_index().rename(columns={"NPN Number": "NPN"})
agg[[c for c in agg.columns if agg[c].dtype == object]] = agg[[c for c in agg.columns if agg[c].dtype == object]].fillna("")
agg["Residency"] = agg["Residency"].map({True: "Resident", False: "Non-Resident"})
types = fl.drop_duplicates(["NPN Number", "License TYCL Desc"]).groupby("NPN Number")["License TYCL Desc"].agg(", ".join)
agg["License Types"] = agg.NPN.map(types).fillna("")
agg["Years of Experience"] = yrs(agg["Earliest License Issue Date"]).fillna(-1).astype(int)
agg["Business Phone"] = agg["Business Phone"].str.replace(r"\D", "", regex=True).str[-10:]
agg["Business Phone"] = agg["Business Phone"].where(agg["Business Phone"].str.len() == 10, "")
agg["Business Phone"] = agg["Business Phone"].map(lambda p: f"({p[:3]}) {p[3:6]}-{p[6:]}" if p else "")
agg["Email"] = agg["Email"].str.strip().str.lower()
print("FL unique people", len(agg), flush=True)
fl_contact = agg.set_index("NPN")[["Email", "Business Phone"]]
fl1 = agg[(agg["Years of Experience"] >= 1) & ((agg.Email != "") | (agg["Business Phone"] != ""))].copy()
fl1["Earliest License Issue Date"] = fl1["Earliest License Issue Date"].dt.date
fl1 = fl1.sort_values(["Years of Experience", "Last Name"], ascending=[False, True])
stats = {"fl_license_rows": len(fl), "fl_people": len(agg),
         "fl_1plus": int((agg["Years of Experience"] >= 1).sum()), "fl_1plus_with_contact": len(fl1)}
del fl

# ---------------- Texas ----------------
URL = ("https://data.texas.gov/resource/kxv3-diwf.json?$select=npn,name,license_type,qualification,"
       "license_issue_date,city,state,pstl_cd&$order=license_number&$limit=50000&$offset={}")
rows, off = [], 0
while True:
    for a in range(5):
        try:
            r = requests.get(URL.format(off), timeout=300); r.raise_for_status(); page = r.json(); break
        except Exception as e:
            print("retry", off, e, flush=True); time.sleep(10 * (a + 1))
    else: raise SystemExit("TX download failed")
    if not page: break
    rows += page; off += len(page); print("TX rows", off, flush=True)
tx = pd.DataFrame(rows).fillna(""); del rows
tx["d"] = pd.to_datetime(tx["license_issue_date"], errors="coerce")
tx["legacy"] = tx["d"].dt.year == 1920
tx = tx[tx.npn != ""].sort_values("d")
tx[["city", "state", "pstl_cd"]] = tx[["city", "state", "pstl_cd"]].replace("", pd.NA)
real = tx[~tx.legacy].groupby("npn")["d"].min()
t = tx.groupby("npn").agg(Name=("name", "first"), City=("city", first), State=("state", first),
        Zip=("pstl_cd", first), legacy=("legacy", "any")).reset_index().rename(columns={"npn": "NPN"})
t[["City", "State", "Zip"]] = t[["City", "State", "Zip"]].fillna("")
for col, src in (("License Types", "license_type"), ("Qualifications", "qualification")):
    t[col] = t.NPN.map(tx.drop_duplicates(["npn", src]).groupby("npn")[src].agg(", ".join)).fillna("")
t["Earliest License Issue Date"] = t.NPN.map(real)
t["Years of Experience"] = yrs(t["Earliest License Issue Date"])
t["Note"] = ""
leg = t.legacy & t["Earliest License Issue Date"].isna()
t.loc[leg, "Note"] = "Legacy TDI record (licensed before electronic records; exact year unknown)"
t.loc[t.legacy & ~leg, "Note"] = "Also holds a legacy TDI record, so true start may be earlier"
t1 = t[(t["Years of Experience"] >= 1) | leg].copy()
t1["Years of Experience"] = t1["Years of Experience"].map(lambda v: "" if pd.isna(v) else int(v))
t1["Earliest License Issue Date"] = t1["Earliest License Issue Date"].dt.date
stats.update({"tx_license_rows": len(tx), "tx_people": len(t), "tx_1plus": len(t1)})
del tx

# contact enrichment: 1) Florida DFS records by NPN  2) user's own lists (High-confidence NPN matches)
t1["Email"] = t1.NPN.map(fl_contact["Email"]).fillna("")
t1["Phone"] = t1.NPN.map(fl_contact["Business Phone"]).fillna("")
t1["Contact Source"] = (t1.Email.ne("") | t1.Phone.ne("")).map({True: "FL DFS record (same NPN)", False: ""})
own = {}
for f in sorted(glob.glob("sheets/results/*with Experience.xlsx")):
    d = pd.read_excel(f, sheet_name=1, dtype=str, keep_default_na=False)
    d = d[d.Confidence == "High"]
    for r in d.itertuples(index=False):
        for npn in re.findall(r"TX TDI \(NPN (\d+)\)", r.Source):
            own.setdefault(npn, (r.Email, r.Phone, os.path.basename(f)))
need = t1.Email.eq("") & t1.Phone.eq("") & t1.NPN.isin(own)
t1.loc[need, "Email"] = t1.loc[need, "NPN"].map(lambda n: own[n][0])
t1.loc[need, "Phone"] = t1.loc[need, "NPN"].map(lambda n: own[n][1])
t1.loc[need, "Contact Source"] = t1.loc[need, "NPN"].map(lambda n: f"Your list: {own[n][2]}")
cols = ["NPN", "Name", "Email", "Phone", "City", "State", "Zip", "License Types", "Qualifications",
        "Earliest License Issue Date", "Years of Experience", "Contact Source", "Note"]
t1 = t1[cols].sort_values("Name")
tc = t1[t1.Email.ne("") | t1.Phone.ne("")]
stats.update({"tx_1plus_with_contact": len(tc), "tx_contact_from_fl": int((tc["Contact Source"] == "FL DFS record (same NPN)").sum())})

# ---------------- write ----------------
files = {
    "Florida_1plus_Years_With_Contacts.csv": fl1,
    "Texas_1plus_Years_With_Contacts.csv": tc,
    "Texas_1plus_Years_All_Licensees_NoPhoneEmail_in_TDI.csv": t1,
}
readme = ["Insurance licensees with MORE THAN 1 YEAR of experience - free official public data",
          f"Built {TODAY.date()}. Years = time since the earliest license issue date on record.", "",
          "Florida: Florida Dept. of Financial Services bulk files 'All Valid Licenses - Individual' (A-K, L-Z).",
          "  One row per person (NPN). Contact details (email, business phone, addresses) come from FL DFS.",
          "  Included only if they have at least an email or a phone.", "",
          "Texas: Texas Dept. of Insurance open data (data.texas.gov kxv3-diwf). TDI publishes NO email/phone,",
          "  only city/state/ZIP. Texas_1plus_Years_With_Contacts adds email/phone from FL DFS (same NPN) or",
          "  from your own uploaded lists (High-confidence matches). The '_All_Licensees' file lists every TX",
          "  licensee with 1+ years, with or without contact details.", "", "Counts:"] + [f"  {k}: {v:,}" for k, v in stats.items()]
zpath = os.path.join(outdir, "FL_TX_Licensees_1plus_Years.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.writestr("README.txt", "\n".join(readme))
    for name, df in files.items():
        z.writestr(name, df.to_csv(index=False))
print("\n".join(readme)); print("zip MB", os.path.getsize(zpath) // 1_000_000)
