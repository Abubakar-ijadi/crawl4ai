"""Build Advocate_Life_Group_Brief.docx from build/brief.html (same content as the PDF).

Usage: python3 html_to_docx.py brief.html out.docx
"""
import sys, re
from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor

NAVY = RGBColor(0x14, 0x32, 0x4A)
TEAL = RGBColor(0x0F, 0x7C, 0x78)
MUTED = RGBColor(0x5B, 0x66, 0x73)
GREEN = RGBColor(0x1E, 0x84, 0x49)
RED = RGBColor(0xC0, 0x39, 0x2B)
AMBER = RGBColor(0xB9, 0x77, 0x0E)
BASE = 9.6
FONT = "Calibri"


def shade(cell_or_par, hex_fill, is_cell=True):
    el = cell_or_par._tc.get_or_add_tcPr() if is_cell else cell_or_par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    el.append(shd)


def para_border(par, color="0F7C78", side="left", sz=12):
    pPr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    for s in ([side] if side != "all" else ["top", "left", "bottom", "right"]):
        e = OxmlElement(f"w:{s}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz)); e.set(qn("w:space"), "4"); e.set(qn("w:color"), color)
        bdr.append(e)
    pPr.append(bdr)


def tight(par, before=0, after=2, line=1.0):
    pf = par.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = line


def add_runs(par, node, size=BASE, color=None, bold=False, italic=False):
    """Recursively add inline content of an HTML node as runs."""
    for ch in node.children:
        if isinstance(ch, NavigableString):
            txt = re.sub(r"\s+", " ", str(ch))
            if not txt:
                continue
            r = par.add_run(txt)
            r.font.size = Pt(size); r.font.name = FONT; r.bold = bold or None; r.italic = italic or None
            if color is not None:
                r.font.color.rgb = color
        elif isinstance(ch, Tag):
            cls = ch.get("class") or []
            if ch.name == "br":
                par.add_run().add_break(); continue
            c = color; s = size; b = bold or ch.name in ("b", "strong"); it = italic or ch.name in ("i", "em")
            if "tag" in cls:
                c = GREEN if "v" in cls else (AMBER if "e" in cls else RGBColor(0x6C, 0x4F, 0xB0))
                s = size - 1; b = True
                ch = BeautifulSoup(f"<span>[{ch.get_text(strip=True)}]</span>", "html.parser").span
            elif "small" in cls:
                c = MUTED; s = size - 0.6
            elif "num" in cls:
                c = TEAL
                ch = BeautifulSoup(f"<span>{ch.get_text(strip=True)}  </span>", "html.parser").span
            elif "pill" in cls or "t" in cls:
                c = TEAL if "pill" in cls else AMBER; b = True
            add_runs(par, ch, s, c, b, it)


def strip_leading(par):
    if par.runs:
        par.runs[0].text = par.runs[0].text.lstrip()


def set_cell_margins(table, top=30, bottom=30, left=60, right=60):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); mar.append(e)
    tblPr.append(mar)


def html_table(doc, t, size):
    rows = t.find_all("tr")
    ncols = max(len(r.find_all(["td", "th"])) for r in rows)
    table = doc.add_table(rows=0, cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_cell_margins(table)
    for r in rows:
        cells = r.find_all(["td", "th"])
        row = table.add_row()
        me = "me" in (r.get("class") or [])
        for i, c in enumerate(cells):
            cell = row.cells[i]
            p = cell.paragraphs[0]; tight(p, 0, 0, 1.0)
            if c.name == "th":
                add_runs(p, c, size - 0.8, MUTED, True)
                shade(cell, "E8EDF1")
            else:
                add_runs(p, c, size, None, me)
                if me:
                    shade(cell, "EEF6F6")
            strip_leading(p)
    # column widths from the header's style="width:N%"; remaining width split evenly
    hdr = rows[0].find_all(["td", "th"])
    pct = []
    for c in hdr:
        m = re.search(r"width:\s*([\d.]+)%", c.get("style") or "")
        pct.append(float(m.group(1)) if m else None)
    known = sum(p for p in pct if p); unknown = [p for p in pct if p is None]
    rest = (100 - known) / len(unknown) if unknown else 0
    pct = [p if p else rest for p in pct]
    table.autofit = False
    grid = table._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(7.5 * 1440 * pct[i] / 100)))
    for i, p in enumerate(pct):
        w = Inches(7.5 * p / 100)
        for row in table.rows:
            row.cells[i].width = w
    # borders: light grey
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for s in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{s}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "D9DEE4"); borders.append(e)
    tblPr.append(borders)
    return table


def card(doc, div, size, title_color=NAVY):
    h3 = div.find("h3")
    p = doc.add_paragraph(); tight(p, 2, 1)
    if h3:
        add_runs(p, h3, size + 0.6, title_color, True); strip_leading(p)
    for li in div.find_all("li"):
        lp = doc.add_paragraph(style="List Bullet"); tight(lp, 0, 1)
        lp.paragraph_format.left_indent = Inches(0.18)
        add_runs(lp, li, size); strip_leading(lp)
    for pp in div.find_all("p"):
        lp = doc.add_paragraph(); tight(lp, 0, 1)
        add_runs(lp, pp, size); strip_leading(lp)


def build(src, out):
    soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.left_margin = sec.right_margin = Inches(0.5)
    sec.top_margin = sec.bottom_margin = Inches(0.4)
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(BASE)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    pages = soup.select("section.page")
    for pi, page in enumerate(pages):
        for el in page.children:
            if not isinstance(el, Tag):
                continue
            cls = el.get("class") or []
            if el.name == "header":
                p = doc.add_paragraph(); tight(p, 0, 3)
                p.paragraph_format.page_break_before = pi > 0
                r = p.add_run(el.select_one(".brand").get_text(strip=True) + "    "); r.bold = True; r.font.size = Pt(8.5); r.font.color.rgb = NAVY; r.font.name = FONT
                r = p.add_run(el.select_one(".meta").get_text(strip=True)); r.font.size = Pt(7); r.font.color.rgb = MUTED; r.font.name = FONT
                para_border(p, "14324A", "bottom", 12)
            elif el.name == "h1":
                p = doc.add_paragraph(); tight(p, 2, 2)
                add_runs(p, el, 14, NAVY, True); strip_leading(p)
            elif el.name == "h2":
                p = doc.add_paragraph(); tight(p, 5, 2)
                add_runs(p, BeautifulSoup(f"<x>{el.get_text(' ', strip=True).upper()}</x>", "html.parser").x, 9, NAVY, True); strip_leading(p)
            elif el.name == "p":
                p = doc.add_paragraph(); tight(p, 0, 3)
                if "defs" in cls:
                    add_runs(p, el, BASE - 0.6, MUTED); para_border(p)
                elif "lede" in cls:
                    add_runs(p, el, BASE - 0.2, MUTED)
                else:
                    add_runs(p, el, BASE - (0.6 if "small" in cls else 0), MUTED if "small" in cls else None)
                strip_leading(p)
            elif el.name == "div" and "exec" in cls:
                for i, li in enumerate(el.find_all("li"), 1):
                    p = doc.add_paragraph(); tight(p, 0, 1); shade(p, "F3F6F8", False)
                    r = p.add_run(f"{i}. "); r.bold = True; r.font.size = Pt(BASE + 0.4); r.font.name = FONT
                    add_runs(p, li, BASE + 0.4)
            elif el.name == "table":
                size = BASE - (0.6 if "comp" in cls or "road" in cls else 0.2)
                html_table(doc, el, size)
            elif el.name == "div" and ("cols" in cls or "two" in cls or "ws" in cls):
                cards = el.find_all("div", class_="card", recursive=False)
                t = doc.add_table(rows=1, cols=len(cards)); set_cell_margins(t, 40, 40, 80, 80)
                tblPr = t._tbl.tblPr; borders = OxmlElement("w:tblBorders")
                for s in ("top", "left", "bottom", "right", "insideV"):
                    e = OxmlElement(f"w:{s}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "D9DEE4"); borders.append(e)
                tblPr.append(borders)
                for i, cd in enumerate(cards):
                    cell = t.rows[0].cells[i]
                    ccls = cd.get("class") or []
                    color = GREEN if "good" in ccls else (RED if "gap" in ccls else NAVY)
                    first = cell.paragraphs[0]; tight(first, 0, 1)
                    h3 = cd.find("h3")
                    if h3:
                        add_runs(first, h3, BASE + 0.4, color, True); strip_leading(first)
                    for li in cd.find_all("li"):
                        lp = cell.add_paragraph(); tight(lp, 0, 1)
                        r = lp.add_run("• "); r.font.size = Pt(BASE - 0.3)
                        add_runs(lp, li, BASE - 0.3)
                    for pp in cd.find_all("p"):
                        lp = cell.add_paragraph(); tight(lp, 0, 1)
                        small = "small" in (pp.get("class") or [])
                        add_runs(lp, pp, BASE - (0.9 if small else 0.3), MUTED if small else None)
                        strip_leading(lp)
            elif el.name == "div" and ("callout" in cls or "first" in cls):
                color_hex = "B9770E" if "callout" in cls else "0F7C78"
                fill = "FDF8EF" if "callout" in cls else "F1F9F8"
                h2 = el.find("h2")
                if h2:
                    p = doc.add_paragraph(); tight(p, 5, 1); shade(p, fill, False); para_border(p, color_hex, "all", 10)
                    add_runs(p, h2, BASE + 0.8, TEAL, True); strip_leading(p)
                lis = el.find_all("li")
                if lis:
                    for li in lis:
                        p = doc.add_paragraph(); tight(p, 0, 1); shade(p, fill, False); para_border(p, color_hex, "all", 10)
                        r = p.add_run("• "); r.font.size = Pt(BASE)
                        add_runs(p, li, BASE)
                else:
                    p = doc.add_paragraph(); tight(p, 5, 2); shade(p, fill, False); para_border(p, color_hex, "all", 10)
                    add_runs(p, el, BASE); strip_leading(p)
            elif el.name == "footer":
                p = doc.add_paragraph(); tight(p, 4, 0)
                add_runs(p, el, BASE - 1.2, MUTED); strip_leading(p); para_border(p, "D9DEE4", "top", 4)
    doc.core_properties.title = "Advocate Life Group: Growth Brief"
    doc.core_properties.author = "Ijadi"
    doc.save(out)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
