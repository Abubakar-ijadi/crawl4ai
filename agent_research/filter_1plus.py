"""Make a workbook with only agents classified 'More than a year', sorted by years."""
import sys, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
src, out = sys.argv[1:3]
r = pd.read_excel(src, sheet_name=1, keep_default_na=False, na_values=[""])
m = r[r["Experience Category"] == "More than a year"].copy()
m["Years of Experience"] = m["Years of Experience"].astype("Int64")
m = m.sort_values(["Years of Experience", "Name"], ascending=[False, True], na_position="first")
wb = Workbook(); ws = wb.active; ws.title = "Agents 1+ Years"
hf, hfill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E78")
cols = list(m.columns); ws.append(cols)
for c in ws[1]: c.font, c.fill, c.alignment = hf, hfill, Alignment(horizontal="center")
for rec in m.itertuples(index=False):
    ws.append([None if v is pd.NA or (isinstance(v, float) and v != v) else v for v in rec])
for j, w in enumerate([26, 16, 34, 7, 18, 11, 11, 40, 90], 1): ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = "A2"; ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
s = wb.create_sheet("Summary", 0)
s["A1"] = "Insurance agents with more than 1 year of experience"; s["A1"].font = Font(bold=True, size=14)
s["A2"] = f"{len(m):,} of {len(r):,} agents, sorted by years (highest first). Source: TX TDI and FL DFS license records."
rows = [("Years", "Agents")]
b = pd.cut(m["Years of Experience"].astype(float), [1, 2, 5, 10, 20, 200], right=False,
           labels=["1-2 yrs", "2-5 yrs", "5-10 yrs", "10-20 yrs", "20+ yrs"]).value_counts().sort_index()
rows += [(k, int(v)) for k, v in b.items()] + [("Legacy record (exact year unknown)", int(m["Years of Experience"].isna().sum())), ("Total", len(m))]
rows += [(), ("Confidence", "Agents")] + [(k, int(v)) for k, v in m.Confidence.value_counts().items()]
rows += [(), ("State", "Agents")] + [(k, int(v)) for k, v in m.State.value_counts().items()]
for i, row in enumerate(rows, start=4):
    for j, v in enumerate(row, 1):
        c = s.cell(i, j, v)
        if row and row[0] in ("Years", "Confidence", "State"): c.font, c.fill = hf, hfill
s.column_dimensions["A"].width = 40
wb.save(out); print("saved", out, len(m))
