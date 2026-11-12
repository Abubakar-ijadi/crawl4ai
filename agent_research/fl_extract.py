"""Download Florida DFS 'All Valid Licenses - Individual' files and keep only rows that
match an agent in the input workbook by email, or by first + last name."""
import csv, gzip, io, json, re, sys, unicodedata
import pandas as pd, requests

links_file, xlsx, out_path = sys.argv[1:4]
import os; os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
links = [l for l in json.load(open(links_file)) if "AllValidLicensesIndividual" in l]
assert links, "no individual license files found"

def toks(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", " ", s.replace("-", " ")).split()

ag = pd.read_excel(xlsx, sheet_name=0)
emails = {str(e).strip().lower() for e in ag.Email.dropna()}
firsts_by_last = {}
for n in ag.Name:
    t = toks(n)
    if len(t) >= 2:
        for last in {t[-1], t[-2] if len(t) > 2 else t[-1]}:
            firsts_by_last.setdefault(last, set()).add(t[0])

kept = 0; header_written = False
with gzip.open(out_path, "wt", newline="") as fo:
    w = csv.writer(fo)
    for url in links:
        print("downloading", url, flush=True)
        with requests.get(url, stream=True, timeout=600, headers={"User-Agent": "Mozilla/5.0"}) as r:
            r.raise_for_status()
            lines = (l.decode("utf-8", "replace") for l in r.iter_lines())
            rd = csv.reader(lines)
            header = next(rd)
            print("columns:", header, flush=True)
            if not header_written:
                w.writerow(["source_file"] + header); header_written = True
            name_cols = [i for i, h in enumerate(header) if "NAME" in h.upper() and "COMPANY" not in h.upper() and "AGENCY" not in h.upper() and "FIRM" not in h.upper()]
            email_cols = [i for i, h in enumerate(header) if "EMAIL" in h.upper()]
            n = 0
            for row in rd:
                n += 1
                hit = any(row[i].strip().lower() in emails for i in email_cols if i < len(row))
                if not hit:
                    t = set(toks(" ".join(row[i] for i in name_cols if i < len(row))))
                    hit = any(firsts_by_last.get(x, set()) & t for x in t)
                if hit:
                    w.writerow([url.rsplit("/", 1)[-1]] + row); kept += 1
            print(f"rows read {n}, kept so far {kept}", flush=True)
print("done, kept", kept)
