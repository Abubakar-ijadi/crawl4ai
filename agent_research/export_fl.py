"""Download Florida DFS 'All Valid Licenses - Individual' files (A-K, L-Z) and save each as
Excel (.xlsx, one sheet each, under Excel's 1,048,576-row limit) and as zipped CSV."""
import csv, io, json, os, sys, zipfile, requests
from openpyxl import Workbook
links_file, outdir = sys.argv[1:3]
os.makedirs(outdir, exist_ok=True)
links = [l for l in json.load(open(links_file)) if "AllValidLicensesIndividual" in l]
assert len(links) == 2, links
for url in links:
    part = "A-K" if "(A-K)" in url else "L-Z"
    raw = os.path.join(outdir, f"Florida_DFS_Valid_Licenses_{part}.csv")
    print("downloading", url, flush=True)
    with requests.get(url, stream=True, timeout=900, headers={"User-Agent": "Mozilla/5.0"}) as r, open(raw, "wb") as f:
        r.raise_for_status()
        for chunk in r.iter_content(1 << 20): f.write(chunk)
    wb = Workbook(write_only=True); ws = wb.create_sheet(f"FL Licenses {part}")
    n = 0
    with open(raw, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f):
            ws.append(row); n += 1
    print(part, "rows incl. header:", n, flush=True)
    assert n <= 1048576, "too many rows for one Excel sheet"
    wb.save(os.path.join(outdir, f"Florida_DFS_Valid_Licenses_{part}.xlsx"))
    with zipfile.ZipFile(raw + ".zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(raw, os.path.basename(raw))
    os.remove(raw)
for f in sorted(os.listdir(outdir)): print(f, os.path.getsize(os.path.join(outdir, f)) // 1_000_000, "MB")
