import sys, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
src, pkl, out = sys.argv[1:4]
res = pd.read_pickle(pkl)
wb = load_workbook(src)
ws = wb.worksheets[0]
hdr = [c.value for c in ws[1]]
assert hdr[:4] == ['Name','Phone','Email','State'], hdr
# sanity: row order unchanged
for i in (2, 500, ws.max_row):
    assert ws.cell(i,1).value == res.Name.iloc[i-2], i
new = ['Experience Category','Years of Experience','Confidence','Source','Notes']
hfont = Font(bold=True, color='FFFFFF'); hfill = PatternFill('solid', fgColor='1F4E78')
fills = {'More than a year':'E2EFDA','Less than a year':'FFF2CC','Not sure':'EDEDED'}
for j, h in enumerate(new, start=5):
    c = ws.cell(1, j, h); c.font = hfont; c.fill = hfill; c.alignment = Alignment(horizontal='center')
for i, r in enumerate(res.itertuples(index=False), start=2):
    cat = r[4]
    ws.cell(i,5,cat).fill = PatternFill('solid', fgColor=fills[cat])
    y = r[5]; ws.cell(i,6, None if pd.isna(y) else int(y))
    ws.cell(i,7,r[6]); ws.cell(i,8,r[7] or None); ws.cell(i,9,r[8])
for j, w in zip(range(1,10), [26,16,34,7,20,11,11,34,90]):
    ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = 'A2'; ws.auto_filter.ref = f'A1:I{ws.max_row}'

# Summary sheet
if 'Summary' in wb.sheetnames: del wb['Summary']
s = wb.create_sheet('Summary', 0)
s['A1'] = 'Insurance Agents - Years of Experience'; s['A1'].font = Font(bold=True, size=14)
s['A2'] = 'As of 2026-11-12. Experience = time since first insurance license issue date found in public state records.'
row = 4
def table(title, df):
    global row
    s.cell(row,1,title).font = Font(bold=True, size=12); row += 1
    for j, h in enumerate(df.columns, 1):
        c = s.cell(row,j,str(h)); c.font = hfont; c.fill = hfill
    row += 1
    for rec in df.itertuples(index=False):
        for j, v in enumerate(rec, 1): s.cell(row,j, v if not isinstance(v,float) or v==v else None)
        row += 1
    row += 1
cats = ['More than a year','Less than a year','Not sure']
vc = res['Experience Category'].value_counts().reindex(cats, fill_value=0)
table('Agents by experience category', pd.DataFrame({'Category':cats,'Agents':vc.values,'Share':[f'{v/len(res):.1%}' for v in vc.values]}))
m = res[res['Experience Category']=='More than a year']['Years of Experience']
bins = pd.cut(m, [0,2,5,10,20,200], right=False, labels=['1-2 yrs','2-5 yrs','5-10 yrs','10-20 yrs','20+ yrs'])
bc = bins.value_counts().reindex(bins.cat.categories, fill_value=0)
table('"More than a year" - breakdown by years', pd.DataFrame({'Years':bc.index.astype(str),'Agents':bc.values}))
ct = pd.crosstab(res['Experience Category'], res['Confidence']).reindex(cats, fill_value=0).reset_index()
table('Confidence of each category', ct)
st = pd.crosstab(res.State, res['Experience Category']).reindex(columns=cats, fill_value=0)
st['Total'] = st.sum(axis=1); st = st.sort_values('Total', ascending=False).reset_index()
table('By state', st)
s.cell(row,1,'How to read Confidence').font = Font(bold=True, size=12); row += 1
for line in [
    'High      - Exact identity match: same email or phone in Florida DFS records, same NPN in both states, or a resident matched to exactly one licensee in their own state.',
    'Medium    - Matched by name + state to exactly one licensee with a fairly rare name (no email/phone confirmation).',
    'Low       - Common name with a possible match only; kept as "Not sure" (possible match in Notes).',
    'No record - No valid license found in Texas or Florida public records.',
    'Years = time since the EARLIEST license issue date found. For agents outside TX/FL it comes from their TX/FL non-resident license, so it is a minimum.',
    'Sources (free, official): Texas Dept. of Insurance open data (data.texas.gov kxv3-diwf, 861K licensees); Florida DFS bulk downloads "All Valid Licenses - Individual" (1.25M license rows), fetched with crawl4ai in GitHub Actions.']:
    s.cell(row,1,line); row += 1
s.column_dimensions['A'].width = 34
for col in 'BCDE': s.column_dimensions[col].width = 18
wb.save(out)
print('saved', out)
