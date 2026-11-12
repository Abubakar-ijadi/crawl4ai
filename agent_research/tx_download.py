"""Download Texas Dept. of Insurance licensee data (data.texas.gov kxv3-diwf), one row per
person (NPN, name, state, earliest license issue date). Free public Socrata API."""
import csv, sys, time, requests
out = sys.argv[1]
URL = ("https://data.texas.gov/resource/kxv3-diwf.json?$select=npn,name,state,"
       "min(license_issue_date)%20as%20d&$group=npn,name,state&$order=npn&$limit=50000&$offset={}")
n = off = 0
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["npn", "name", "state", "d"])
    while True:
        for attempt in range(5):
            try:
                r = requests.get(URL.format(off), timeout=300); r.raise_for_status(); rows = r.json(); break
            except Exception as e:
                print("retry", off, e, flush=True); time.sleep(10 * (attempt + 1))
        else:
            raise SystemExit("TX download failed")
        if not rows: break
        for x in rows: w.writerow([x.get("npn"), x.get("name"), x.get("state"), x.get("d")])
        n += len(rows); off += len(rows); print("TX rows", n, flush=True)
print("done", n)
