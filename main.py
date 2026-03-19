import streamlit as st
import io
import json
import numpy as np
import ezdxf
from ezdxf import units as dxf_units
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath
import datetime
import re

st.set_page_config(page_title="ARBURG Zone Diagram Generator", layout="wide")

# ═══════════════════════════════════════════════════════════════════════════════
#  LANGUAGE PACKAGES
# ═══════════════════════════════════════════════════════════════════════════════
LANG = {
    "SL": {
        "app_title":        "🔌 Generator sheme con ARBURG",
        "app_sub":          "Konfigurirajte grelne cone in izvozite SVG / DXF.",
        "general":          "⚙️ Splošne nastavitve",
        "diag_title":       "Naziv diagrama",
        "tool_number":      "Številka orodja",
        "num_zones":        "Število con",
        "zone_width":       "Širina cone (px / mm)",
        "svg_height":       "Višina diagrama (px)",
        "symbol":           "📐 Nastavitve simbolov",
        "show_pol":         "Prikaži oznake +/−",
        "show_zlbl":        "Prikaži oznake con",
        "show_wattage":     "Prikaži moči grelcev",
        "show_date":        "Prikaži datum",
        "grp_diagram":      "📋 Diagram",
        "grp_layout":       "📐 Postavitev",
        "grp_symbols":      "🔣 Simboli",
        "grp_fonts":        "🔤 Pisave",
        "grp_colors":       "🎨 Barve",
        "grp_plate":        "🪛 Ploščica (laser)",
        "grp_templates":    "💾 Predloge",
        "dividers":         "Notranje črte grelca",
        "style":            "🎨 Slog",
        "stroke_col":       "Barva linij",
        "bg_col":           "Barva ozadja",
        "inact_col":        "Barva križa (neaktivno)",
        "font_sz":          "Velikost pisave terminalov",
        "font_sz_lbl":      "Velikost pisave oznak con / moči",
        "font_sz_meta":     "Velikost pisave datum / orodje",
        "num_scheme":       "Shema številčenja terminalov",
        "seq_label":        "Zaporedno (1-2, 3-4 … grelec; 13-14 … TC)",
        "custom_label":     "Po meri (ročni vnos)",
        "per_zone":         "Konfiguracija po conah",
        "zone_hdr":         "Cona",
        "active_lbl":       "Aktivna",
        "wattage_lbl":      "Moč",
        "wattage_def":      "350 W",
        "zone_type_lbl":    "Tip cone",
        "type_nozzle":      "VSTOPNA SOBA",
        "type_block":       "GRELNI BLOK",
        "type_heater":      "GRELEC",
        "warn_nozzle":      "⚠️ VSTOPNA ŠOBA je že dodeljena coni {z}.",
        "warn_block":       "⚠️ GRELNI BLOK je že dodeljen coni {z}.",
        "h_plus":           "G+",
        "h_minus":          "G−",
        "tc_plus":          "TC+",
        "tc_minus":         "TC−",
        "preview":          "Predogled",
        "dl_svg":           "⬇️  Prenesi SVG",
        "dl_dxf":           "⬇️  Prenesi DXF",
        "tip":              "Nasvet: SVG odprite v Inkscape, DXF v AutoCAD / LibreCAD.",
        "templates":        "💾 Predloge",
        "save_tpl":         "Shrani konfiguracijo",
        "load_tpl":         "Naloži konfiguracijo",
        "tpl_name":         "Ime predloge",
        "tpl_saved":        "✅ Predloga shranjena.",
        "tpl_loaded":       "✅ Predloga naložena.",
        "tpl_empty":        "Ni shranjenih predlog.",
        "delete_tpl":       "Izbriši",
        "tc_type_lbl":      "Tip TC",
        "date_label":       "Datum",
        "plate_section":    "📐 Skaliranje na ploščico",
        "plate_enable":     "Omogoči skaliranje na ploščico",
        "plate_w":          "Širina ploščice (mm)",
        "plate_h":          "Višina ploščice (mm)",
        "plate_margin":     "Rob (mm)",
        "plate_info":       "ℹ️ Gravura: {w:.1f} × {h:.1f} mm  |  Merilo: 1 px = {s:.4f} mm",
        "plate_warn":       "⚠️ Diagram je večji od razpoložljivega območja — poveča rob ali ploščico.",
        "plate_border":     "Nariši okvir ploščice v DXF",
    },
    "EN": {
        "app_title":        "🔌 ARBURG Zone Diagram Generator",
        "app_sub":          "Configure heating zones and export as SVG / DXF.",
        "general":          "⚙️ General Settings",
        "diag_title":       "Diagram title",
        "tool_number":      "Tool number",
        "num_zones":        "Number of zones",
        "zone_width":       "Zone width (px / mm)",
        "svg_height":       "Diagram height (px)",
        "symbol":           "📐 Symbol Settings",
        "show_pol":         "Show +/− polarity labels",
        "show_zlbl":        "Show zone labels",
        "show_wattage":     "Show heater wattage",
        "show_date":        "Show date",
        "grp_diagram":      "📋 Diagram",
        "grp_layout":       "📐 Layout",
        "grp_symbols":      "🔣 Symbols",
        "grp_fonts":        "🔤 Fonts",
        "grp_colors":       "🎨 Colors",
        "grp_plate":        "🪛 Plate (laser)",
        "grp_templates":    "💾 Templates",
        "dividers":         "Heater internal dividers",
        "style":            "🎨 Style",
        "stroke_col":       "Line / stroke color",
        "bg_col":           "Background color",
        "inact_col":        "Inactive cross color",
        "font_sz":          "Terminal number font size",
        "font_sz_lbl":      "Zone label / wattage font size",
        "font_sz_meta":     "Date / tool font size",
        "num_scheme":       "Terminal numbering scheme",
        "seq_label":        "Sequential pairs (1-2, 3-4 … heater; 13-14 … TC)",
        "custom_label":     "Custom (enter manually)",
        "per_zone":         "Per-zone configuration",
        "zone_hdr":         "Zone",
        "active_lbl":       "Active",
        "wattage_lbl":      "Wattage",
        "wattage_def":      "350 W",
        "zone_type_lbl":    "Zone type",
        "type_nozzle":      "NOZZLE",
        "type_block":       "HEATING BLOCK",
        "type_heater":      "HEATER",
        "warn_nozzle":      "⚠️ NOZZLE already assigned to zone {z}.",
        "warn_block":       "⚠️ HEATING BLOCK already assigned to zone {z}.",
        "h_plus":           "H+",
        "h_minus":          "H−",
        "tc_plus":          "TC+",
        "tc_minus":         "TC−",
        "preview":          "Preview",
        "dl_svg":           "⬇️  Download SVG",
        "dl_dxf":           "⬇️  Download DXF",
        "tip":              "Tip: open SVG in Inkscape, DXF in AutoCAD / LibreCAD.",
        "templates":        "💾 Templates",
        "save_tpl":         "Save configuration",
        "load_tpl":         "Load configuration",
        "tpl_name":         "Template name",
        "tpl_saved":        "✅ Template saved.",
        "tpl_loaded":       "✅ Template loaded.",
        "tpl_empty":        "No saved templates.",
        "delete_tpl":       "Delete",
        "tc_type_lbl":      "TC type",
        "date_label":       "Date",
        "plate_section":    "📐 Scale to plate",
        "plate_enable":     "Enable plate scaling",
        "plate_w":          "Plate width (mm)",
        "plate_h":          "Plate height (mm)",
        "plate_margin":     "Margin (mm)",
        "plate_info":       "ℹ️ Engraving: {w:.1f} × {h:.1f} mm  |  Scale: 1 px = {s:.4f} mm",
        "plate_warn":       "⚠️ Diagram exceeds available area — increase margin or plate size.",
        "plate_border":     "Draw plate border in DXF",
    }
}

TC_TYPES = ["J", "K", "T", "E", "N", "R", "S", "B"]

# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT → SVG PATH  (matplotlib backend, no <text> elements)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _build_svg_path(text, cx, cy, font_size, anchor, fill):
    fp  = FontProperties(family='DejaVu Sans')
    mtp = TextPath((0, 0), text, size=font_size, prop=fp)
    bb  = mtp.get_extents()
    tw  = bb.x1 - bb.x0
    if anchor == 'middle':
        ox = cx - tw / 2 - bb.x0
    elif anchor == 'end':
        ox = cx - tw - bb.x0
    else:
        ox = cx - bb.x0
    oy = cy + (bb.y0 + bb.y1) / 2

    verts = mtp.vertices
    codes = mtp.codes
    d = []
    i = 0
    n = len(codes)
    while i < n:
        code = codes[i]
        vx, vy = verts[i]
        sx = vx + ox
        sy = oy - vy
        if code == MplPath.MOVETO:
            d.append(f'M {sx:.2f},{sy:.2f}')
            i += 1
        elif code == MplPath.LINETO:
            d.append(f'L {sx:.2f},{sy:.2f}')
            i += 1
        elif code == MplPath.CURVE3:
            vx2, vy2 = verts[i+1]
            d.append(f'Q {sx:.2f},{sy:.2f} {vx2+ox:.2f},{oy-vy2:.2f}')
            i += 2
        elif code == MplPath.CURVE4:
            vx2, vy2 = verts[i+1]
            vx3, vy3 = verts[i+2]
            d.append(f'C {sx:.2f},{sy:.2f} {vx2+ox:.2f},{oy-vy2:.2f} {vx3+ox:.2f},{oy-vy3:.2f}')
            i += 3
        elif code == MplPath.CLOSEPOLY:
            d.append('Z')
            i += 1
        else:
            i += 1
    return f'<path d="{" ".join(d)}" fill="{fill}" stroke="none"/>'

def tp(text, cx, cy, font_size, anchor='middle', fill='#444444'):
    if not str(text).strip():
        return ''
    return _build_svg_path(str(text), cx, cy, font_size, anchor, fill)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT → DXF POLYLINES  (bezier approximated, no MTEXT)
# ═══════════════════════════════════════════════════════════════════════════════
def add_text_dxf(msp, text, cx, cy, font_size, color=7):
    if not str(text).strip():
        return
    fp  = FontProperties(family='DejaVu Sans')
    mtp = TextPath((0, 0), str(text), size=font_size, prop=fp)
    bb  = mtp.get_extents()
    tw  = bb.x1 - bb.x0
    ox  = cx - tw / 2 - bb.x0
    oy  = cy - (bb.y0 + bb.y1) / 2

    verts = mtp.vertices
    codes = mtp.codes
    i = 0
    n = len(codes)
    current = []

    def flush(pts):
        if len(pts) >= 2:
            msp.add_lwpolyline(pts, dxfattribs={'color': color, 'closed': False})

    while i < n:
        code = codes[i]
        vx, vy = verts[i]
        px = vx + ox
        py = vy + oy
        if code == MplPath.MOVETO:
            flush(current)
            current = [(px, py)]
            i += 1
        elif code == MplPath.LINETO:
            current.append((px, py))
            i += 1
        elif code == MplPath.CURVE3:
            p0 = current[-1] if current else (px, py)
            vx2, vy2 = verts[i+1]
            p1 = (px, py)
            p2 = (vx2 + ox, vy2 + oy)
            for t in np.linspace(0, 1, 8)[1:]:
                bx = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
                by = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
                current.append((bx, by))
            i += 2
        elif code == MplPath.CURVE4:
            p0 = current[-1] if current else (px, py)
            vx2, vy2 = verts[i+1]
            vx3, vy3 = verts[i+2]
            p1 = (px, py)
            p2 = (vx2 + ox, vy2 + oy)
            p3 = (vx3 + ox, vy3 + oy)
            for t in np.linspace(0, 1, 10)[1:]:
                bx = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
                by = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
                current.append((bx, by))
            i += 3
        elif code == MplPath.CLOSEPOLY:
            if current:
                current.append(current[0])
            flush(current)
            current = []
            i += 1
        else:
            i += 1
    flush(current)


# ═══════════════════════════════════════════════════════════════════════════════
#  CORE DIAGRAM BUILDER
# ═══════════════════════════════════════════════════════════════════════════════
def build_elements(
    zones, title, tool_number, date_str,
    zone_w, svg_h, show_pol, show_zlbl, dividers,
    font_num=None, font_lbl=None, font_meta=None,
    show_wattage=True, tool_label_prefix="Tool"
):
    """Returns a list of abstract drawing elements (dicts) shared by SVG & DXF."""
    svg_w = zone_w * len(zones) + 4

    H_CX  = zone_w * 30 // 100
    T_CX  = zone_w * 70 // 100
    TOP_Y = int(svg_h * 0.145)
    BOT_Y = int(svg_h * 0.810)
    CR    = int(zone_w * 0.125)

    HR_TOP = int(svg_h * 0.232)
    HR_H   = int(svg_h * 0.483)
    HR_W   = int(zone_w * 0.226)
    HR_X   = H_CX - HR_W // 2

    CT  = int(svg_h * 0.380)
    CB  = int(svg_h * 0.560)
    JY  = (CT + CB) // 2
    TDX = int(zone_w * 0.109)

    CPX = int(zone_w * 0.06)
    CRT = int(svg_h * 0.10)
    CRB = int(svg_h * 0.90)

    FS_NUM   = font_num if font_num else int(zone_w * 0.094)
    FS_TITLE = int(svg_h * 0.076)
    FS_LBL   = font_lbl if font_lbl else int(svg_h * 0.029)
    FS_POL   = int(svg_h * 0.033)
    FS_META  = font_meta if font_meta else int(svg_h * 0.022)
    JR       = max(5, int(zone_w * 0.027))

    E = []

    def line(x1, y1, x2, y2, layer='LINES', lw=1.8):
        E.append({'t': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'layer': layer, 'lw': lw})

    def circle(cx, cy, r, layer='CIRCLES'):
        E.append({'t': 'circle', 'cx': cx, 'cy': cy, 'r': r, 'layer': layer})

    def rect(x, y, w, h, layer='HEATER'):
        E.append({'t': 'rect', 'x': x, 'y': y, 'w': w, 'h': h, 'layer': layer})

    def text(s, cx, cy, fs, anchor='middle', layer='TEXT'):
        E.append({'t': 'text', 's': str(s), 'cx': cx, 'cy': cy, 'fs': fs, 'anchor': anchor, 'layer': layer})

    def cross(x0, y0, x1, y1, layer='INACTIVE'):
        E.append({'t': 'cross', 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'layer': layer})

    # Title
    text(title, svg_w // 2, int(svg_h * 0.055), FS_TITLE, 'middle', 'TITLE')

    # Tool number + date at top
    meta_y = int(svg_h * 0.020) + FS_META

    if tool_number:
        text(f"{tool_label_prefix}: {tool_number}", 8, meta_y, FS_META, 'start', 'META')

    if date_str:
        text(date_str, svg_w - 8, meta_y, FS_META, 'end', 'META')

    for i, (t1, t2, t3, t4, zlabel, tc_type, active, wattage) in enumerate(zones):
        ox  = i * zone_w + 2
        hx  = ox + H_CX
        tx  = ox + T_CX
        mid = ox + (H_CX + T_CX) // 2

        if i > 0:
            line(ox - 2, 0, ox - 2, svg_h, 'SEP', 1.5)

        # Heater
        circle(hx, TOP_Y, CR, 'TERMINALS')
        text(t1, hx, TOP_Y, FS_NUM, 'middle', 'TERMINALS_TXT')
        line(hx, TOP_Y + CR, hx, HR_TOP)
        rect(ox + HR_X, HR_TOP, HR_W, HR_H)

        if dividers > 0:
            step = HR_H / (dividers + 1)
            for d in range(1, dividers + 1):
                dy = int(HR_TOP + step * d)
                line(ox + HR_X + 4, dy, ox + HR_X + HR_W - 4, dy, 'HEATER_DIV')

        line(hx, HR_TOP + HR_H, hx, BOT_Y - CR)
        circle(hx, BOT_Y, CR, 'TERMINALS')
        text(t2, hx, BOT_Y, FS_NUM, 'middle', 'TERMINALS_TXT')

        # TC
        circle(tx, TOP_Y, CR, 'TERMINALS')
        text(t3, tx, TOP_Y, FS_NUM, 'middle', 'TERMINALS_TXT')
        if show_pol:
            text('+', tx + CR // 2 + FS_POL // 2, int(svg_h * 0.270), FS_POL, 'start', 'POLARITY')

        line(tx, TOP_Y + CR, tx, CT, 'TC')
        E.append({'t': 'polyline', 'pts': [(tx, CT), (tx + TDX, JY)], 'layer': 'TC'})
        circle(tx + TDX, JY, JR, 'TC_JUNC')
        E.append({'t': 'polyline', 'pts': [(tx + TDX, JY), (tx, CB)], 'layer': 'TC'})
        line(tx, CB, tx, BOT_Y - CR, 'TC')

        if show_pol:
            text('-', tx + CR // 2 + FS_POL // 2, int(svg_h * 0.724), FS_POL, 'start', 'POLARITY')

        circle(tx, BOT_Y, CR, 'TERMINALS')
        text(t4, tx, BOT_Y, FS_NUM, 'middle', 'TERMINALS_TXT')

        if not active:
            cross(ox + CPX, CRT, ox + zone_w - CPX, CRB, 'INACTIVE')

        zlbl_y = int(svg_h * 0.955)
        if show_zlbl and active:
            text(zlabel, mid, zlbl_y, FS_LBL, 'middle', 'ZONE_LBL')
        if active and show_wattage and str(wattage).strip():
            wat_y = zlbl_y + int(FS_LBL * 1.2)
            text(wattage, mid, wat_y, FS_LBL, 'middle', 'WATTAGE')

    return E, svg_w


# ═══════════════════════════════════════════════════════════════════════════════
#  SVG RENDERER
# ═══════════════════════════════════════════════════════════════════════════════
def render_svg(elements, svg_w, svg_h, stroke, bg, inactive_col,
               phys_w_mm=None, phys_h_mm=None, vb_h=None):
    vb_height = vb_h if vb_h else svg_h
    w_attr = f"{phys_w_mm:.2f}mm" if phys_w_mm else str(svg_w)
    h_attr = f"{phys_h_mm:.2f}mm" if phys_h_mm else str(svg_h)

    L = []
    L.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_w} {vb_height}" width="{w_attr}" height="{h_attr}" '
        f'style="background:{bg}">'
    )
    L.append(
        f'<defs><style>'
        f'line,polyline{{stroke:{stroke};fill:none;stroke-width:1.8;}}'
        f'rect.heater{{fill:{bg};stroke:{stroke};stroke-width:1.8;}}'
        f'circle{{fill:{bg};stroke:{stroke};stroke-width:1.8;}}'
        f'.cross{{stroke:{inactive_col};stroke-width:4;stroke-linecap:round;opacity:0.85;}}'
        f'</style></defs>'
    )

    for e in elements:
        t = e['t']
        if t == 'line':
            lw = e.get('lw', 1.8)
            col = inactive_col if e['layer'] == 'INACTIVE' else stroke
            L.append(
                f'<line x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" '
                f'stroke="{col}" stroke-width="{lw}"/>'
            )
        elif t == 'circle':
            L.append(
                f'<circle cx="{e["cx"]}" cy="{e["cy"]}" r="{e["r"]}" '
                f'fill="{bg}" stroke="{stroke}" stroke-width="1.8"/>'
            )
        elif t == 'rect':
            L.append(
                f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" '
                f'fill="{bg}" stroke="{stroke}" stroke-width="1.8"/>'
            )
        elif t == 'polyline':
            pts = ' '.join(f'{x},{y}' for x, y in e['pts'])
            L.append(f'<polyline points="{pts}" stroke="{stroke}" fill="none" stroke-width="1.8"/>')
        elif t == 'cross':
            L.append(f'<line x1="{e["x0"]}" y1="{e["y0"]}" x2="{e["x1"]}" y2="{e["y1"]}" class="cross"/>')
            L.append(f'<line x1="{e["x1"]}" y1="{e["y0"]}" x2="{e["x0"]}" y2="{e["y1"]}" class="cross"/>')
        elif t == 'text':
            L.append(tp(e['s'], e['cx'], e['cy'], e['fs'], e['anchor'], stroke))

    L.append('</svg>')
    return '\n'.join(L)


# ═══════════════════════════════════════════════════════════════════════════════
#  DXF RENDERER
# ═══════════════════════════════════════════════════════════════════════════════
def render_dxf(elements, svg_w, svg_h, stroke,
               dxf_scale=0.1, offset_x=0.0, offset_y=0.0,
               plate_w_mm=None, plate_h_mm=None, draw_border=False):
    doc = ezdxf.new('R2010')
    doc.units = dxf_units.MM

    layer_defs = {
        'LINES':         (7, 0.18),
        'SEP':           (7, 0.15),
        'TERMINALS':     (7, 0.18),
        'TERMINALS_TXT': (7, 0.18),
        'HEATER':        (7, 0.18),
        'HEATER_DIV':    (7, 0.13),
        'TC':            (7, 0.18),
        'TC_JUNC':       (7, 0.18),
        'TC_TYPE':       (3, 0.13),
        'POLARITY':      (7, 0.13),
        'INACTIVE':      (1, 0.35),
        'TITLE':         (7, 0.35),
        'META':          (8, 0.13),
        'ZONE_LBL':      (7, 0.18),
        'WATTAGE':       (7, 0.18),
    }
    for lname, (col, lw) in layer_defs.items():
        if lname not in doc.layers:
            doc.layers.add(lname, color=col, lineweight=int(lw * 100))

    msp = doc.modelspace()

    def fy(y):
        return svg_h - y

    def ds(v):
        return v * dxf_scale

    def tx_(x):
        return ds(x) + offset_x

    def ty_(y):
        return ds(fy(y)) + offset_y

    if draw_border and plate_w_mm and plate_h_mm:
        if 'PLATE_BORDER' not in doc.layers:
            doc.layers.add('PLATE_BORDER', color=3, lineweight=25)
        msp.add_lwpolyline(
            [(0, 0), (plate_w_mm, 0), (plate_w_mm, plate_h_mm), (0, plate_h_mm), (0, 0)],
            dxfattribs={'layer': 'PLATE_BORDER'}
        )

    for e in elements:
        t = e['t']
        lay = e.get('layer', 'LINES')
        att = {'layer': lay}

        if t == 'line':
            msp.add_line((tx_(e['x1']), ty_(e['y1'])), (tx_(e['x2']), ty_(e['y2'])), dxfattribs=att)
        elif t == 'circle':
            msp.add_circle((tx_(e['cx']), ty_(e['cy'])), ds(e['r']), dxfattribs=att)
        elif t == 'rect':
            x, y, w, h = e['x'], e['y'], e['w'], e['h']
            pts = [
                (tx_(x), ty_(y)),
                (tx_(x + w), ty_(y)),
                (tx_(x + w), ty_(y + h)),
                (tx_(x), ty_(y + h)),
                (tx_(x), ty_(y)),
            ]
            msp.add_lwpolyline(pts, dxfattribs=att)
        elif t == 'polyline':
            pts = [(tx_(x), ty_(y)) for x, y in e['pts']]
            msp.add_lwpolyline(pts, dxfattribs=att)
        elif t == 'cross':
            msp.add_line((tx_(e['x0']), ty_(e['y0'])), (tx_(e['x1']), ty_(e['y1'])), dxfattribs=att)
            msp.add_line((tx_(e['x1']), ty_(e['y0'])), (tx_(e['x0']), ty_(e['y1'])), dxfattribs=att)
        elif t == 'text':
            add_text_dxf(
                msp,
                e['s'],
                tx_(e['cx']),
                ty_(e['cy']),
                ds(e['fs']),
                color=layer_defs.get(lay, (7,))[0]
            )

    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue().encode('utf-8')


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if 'templates' not in st.session_state:
    st.session_state['templates'] = {}


# ═══════════════════════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    lang_choice = st.selectbox("🌐 Jezik / Language", ["SL", "EN"], index=0)

T = LANG[lang_choice]
tool_label_prefix = "Orodje" if lang_choice == "SL" else "Tool"

st.title(T["app_title"])
st.markdown(T["app_sub"])

with st.sidebar:
    with st.expander(T["grp_diagram"], expanded=True):
        title_text  = st.text_input(T["diag_title"], value="ARBURG")
        tool_number = st.text_input(T["tool_number"], value="")

    with st.expander(T["grp_layout"], expanded=True):
        num_zones  = st.slider(T["num_zones"], 1, 12, 6)
        zone_width = st.slider(T["zone_width"], 180, 320, 256)
        svg_height = st.slider(T["svg_height"], 400, 800, 580)

    with st.expander(T["grp_symbols"], expanded=True):
        show_polarity   = st.checkbox(T["show_pol"], value=True)
        show_zone_lbl   = st.checkbox(T["show_zlbl"], value=True)
        show_wattage    = st.checkbox(T["show_wattage"], value=True)
        show_date       = st.checkbox(T["show_date"], value=True)
        heater_dividers = st.slider(T["dividers"], 0, 5, 3)

    with st.expander(T["grp_fonts"], expanded=False):
        font_size_num  = st.slider(T["font_sz"], 14, 36, 24)
        font_size_lbl  = st.slider(T["font_sz_lbl"], 8, 35, 24)
        font_size_meta = st.slider(T["font_sz_meta"], 6, 30, 12)

    with st.expander(T["grp_colors"], expanded=False):
        stroke_color   = st.color_picker(T["stroke_col"], value="#444444")
        bg_color       = st.color_picker(T["bg_col"], value="#ffffff")
        inactive_color = st.color_picker(T["inact_col"], value="#cc0000")

    with st.expander(T["grp_plate"], expanded=False):
        plate_enable = st.checkbox(T["plate_enable"], value=False)
        plate_w_mm   = st.number_input(T["plate_w"], min_value=10.0, max_value=2000.0, value=300.0, step=5.0)
        plate_h_mm   = st.number_input(T["plate_h"], min_value=10.0, max_value=2000.0, value=150.0, step=5.0)
        plate_margin = st.number_input(T["plate_margin"], min_value=0.0, max_value=50.0, value=5.0, step=0.5)
        plate_border = st.checkbox(T["plate_border"], value=False, disabled=not plate_enable)

    with st.expander(T["grp_templates"], expanded=False):
        tpl_name = st.text_input(T["tpl_name"], value="")

    st.markdown(
        """
        <style>
        .sb-footer {
            margin-top: 1.5rem;
            padding: 0.7rem 0 0.2rem 0;
            border-top: 1px solid rgba(128,128,128,0.2);
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        .sb-footer-title {
            font-size: 0.70rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: var(--text-color);
            opacity: 0.75;
        }
        .sb-footer-badge {
            font-family: monospace;
            font-size: 0.60rem;
            color: var(--text-color);
            opacity: 0.45;
            border: 1px solid currentColor;
            border-radius: 3px;
            padding: 0px 4px;
            margin-left: 5px;
            vertical-align: middle;
        }
        .sb-footer-sub {
            margin-top: 3px;
            font-size: 0.68rem;
            color: var(--text-color);
            opacity: 0.45;
        }
        .sb-footer-name {
            opacity: 1 !important;
            font-weight: 600;
            color: var(--text-color);
            opacity: 0.65;
        }
        .sb-footer-copy {
            margin-top: 1px;
            font-size: 0.60rem;
            color: var(--text-color);
            opacity: 0.28;
        }
        </style>
        <div class="sb-footer">
            <div>
                <span class="sb-footer-title">ARBURG Zone Generator</span>
                <span class="sb-footer-badge">v1.0</span>
            </div>
            <div class="sb-footer-sub">
                Made by <span class="sb-footer-name">Dejan Rožič</span>
            </div>
            <div class="sb-footer-copy">© 2026 · All rights reserved</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─── Terminal numbering ───────────────────────────────────────────────────────
st.subheader(T["num_scheme"])
num_scheme = st.radio(
    "",
    [T["seq_label"], T["custom_label"]],
    horizontal=True,
    label_visibility="collapsed"
)

# ─── Per-zone config ──────────────────────────────────────────────────────────
st.subheader(T["per_zone"])

ZONE_TYPES = [T["type_nozzle"], T["type_block"], T["type_heater"]]

zone_configs       = []
nozzle_assigned_to = None
block_assigned_to  = None
heater_counter     = 0

cols_per_row = min(num_zones, 6)
rows_needed  = (num_zones + cols_per_row - 1) // cols_per_row
col_sets     = [st.columns(cols_per_row) for _ in range(rows_needed)]

for z in range(num_zones):
    row   = z // cols_per_row
    col_i = z % cols_per_row
    with col_sets[row][col_i]:
        st.markdown(f"**{T['zone_hdr']} {z+1}**")

        zone_type = st.selectbox(T["zone_type_lbl"], ZONE_TYPES, index=2, key=f"ztype{z}")

        if zone_type == T["type_nozzle"]:
            if nozzle_assigned_to is not None:
                st.warning(T["warn_nozzle"].format(z=nozzle_assigned_to))
            else:
                nozzle_assigned_to = z + 1
        elif zone_type == T["type_block"]:
            if block_assigned_to is not None:
                st.warning(T["warn_block"].format(z=block_assigned_to))
            else:
                block_assigned_to = z + 1

        if zone_type == T["type_nozzle"]:
            svg_label = T["type_nozzle"]
        elif zone_type == T["type_block"]:
            svg_label = T["type_block"]
        else:
            heater_counter += 1
            svg_label = f"{T['type_heater']} {heater_counter}"

        active = st.checkbox(T["active_lbl"], value=True, key=f"act{z}")
        wattage = ""
        if active:
            wattage = st.text_input(T["wattage_lbl"], value=T["wattage_def"], key=f"wat{z}")

        if num_scheme == T["custom_label"]:
            h_top = st.number_input(T["h_plus"], value=z*2+1, key=f"ht{z}", step=1)
            h_bot = st.number_input(T["h_minus"], value=z*2+2, key=f"hb{z}", step=1)
            t_top = st.number_input(T["tc_plus"], value=z*2+1+num_zones*2, key=f"tt{z}", step=1)
            t_bot = st.number_input(T["tc_minus"], value=z*2+2+num_zones*2, key=f"tb{z}", step=1)
            zone_configs.append((
                int(h_top), int(h_bot), int(t_top), int(t_bot),
                svg_label, 'J', active, wattage
            ))
        else:
            zone_configs.append((
                z*2+1, z*2+2,
                z*2+1+num_zones*2, z*2+2+num_zones*2,
                svg_label, 'J', active, wattage
            ))

# ─── Template save / load ─────────────────────────────────────────────────────
date_str = datetime.date.today().strftime("%d.%m.%Y") if show_date else ""

tpl_cfg = {
    "title": title_text,
    "tool_number": tool_number,
    "num_zones": num_zones,
    "zone_width": zone_width,
    "svg_height": svg_height,
    "show_polarity": show_polarity,
    "show_zone_lbl": show_zone_lbl,
    "show_wattage": show_wattage,
    "show_date": show_date,
    "heater_dividers": heater_dividers,
    "stroke_color": stroke_color,
    "bg_color": bg_color,
    "inactive_color": inactive_color,
    "font_size_num": font_size_num,
    "font_size_lbl": font_size_lbl,
    "font_size_meta": font_size_meta,
    "zones": [list(z) for z in zone_configs],
}

col_sv, col_dl_tpl = st.columns(2)
with col_sv:
    if st.button(T["save_tpl"]) and tpl_name.strip():
        st.session_state['templates'][tpl_name.strip()] = tpl_cfg
        st.success(T["tpl_saved"])

saved = st.session_state['templates']
if saved:
    with col_dl_tpl:
        dl_tpl_name = st.selectbox(T["load_tpl"], list(saved.keys()))
    c1, c2 = st.columns(2)
    with c1:
        tpl_json = json.dumps(saved[dl_tpl_name], ensure_ascii=False, indent=2)
        st.download_button("⬇️ JSON", tpl_json.encode(), f"{dl_tpl_name}.json", "application/json")
    with c2:
        if st.button(T["delete_tpl"]):
            del st.session_state['templates'][dl_tpl_name]
            st.rerun()
else:
    st.caption(T["tpl_empty"])

# ─── Generate elements ────────────────────────────────────────────────────────
elements, svg_w = build_elements(
    zone_configs,
    title_text,
    tool_number,
    date_str,
    zone_width,
    svg_height,
    show_polarity,
    show_zone_lbl,
    heater_dividers,
    font_num=font_size_num,
    font_lbl=font_size_lbl,
    font_meta=font_size_meta,
    show_wattage=show_wattage,
    tool_label_prefix=tool_label_prefix
)

# ─── Plate scale calculation ──────────────────────────────────────────────────
avail_w_mm = plate_w_mm - 2 * plate_margin
avail_h_mm = plate_h_mm - 2 * plate_margin

if plate_enable and avail_w_mm > 0 and avail_h_mm > 0:
    scale_x = avail_w_mm / svg_w
    scale_y = avail_h_mm / svg_height
    dxf_scale  = min(scale_x, scale_y)
    engraved_w = svg_w * dxf_scale
    engraved_h = svg_height * dxf_scale
    offset_x = plate_margin + (avail_w_mm - engraved_w) / 2
    offset_y = plate_margin + (avail_h_mm - engraved_h) / 2
    phys_w_mm = plate_w_mm
    phys_h_mm = plate_h_mm

    st.info(T["plate_info"].format(w=engraved_w, h=engraved_h, s=dxf_scale))
    if scale_x > 1.05 or scale_y > 1.05:
        st.warning(T["plate_warn"])
else:
    dxf_scale = 0.1
    offset_x = 0.0
    offset_y = 0.0
    phys_w_mm = None
    phys_h_mm = None

# Bottom padding so large bottom fonts never get clipped
export_pad = int(font_size_lbl * 2.5)
vb_h_padded = svg_height + export_pad

# ─── Render export SVG ────────────────────────────────────────────────────────
svg_str = render_svg(
    elements, svg_w, svg_height,
    stroke_color, bg_color, inactive_color,
    phys_w_mm=phys_w_mm, phys_h_mm=phys_h_mm, vb_h=vb_h_padded
)

# ─── Render preview SVG ───────────────────────────────────────────────────────
svg_preview = render_svg(
    elements, svg_w, svg_height,
    stroke_color, bg_color, inactive_color,
    phys_w_mm=None, phys_h_mm=None, vb_h=vb_h_padded
)
svg_preview = re.sub(
    r'width="[^"]*"\s*height="[^"]*"',
    'width="100%" height="auto" style="display:block"',
    svg_preview,
    count=1
)

st.markdown("---")
st.subheader(T["preview"])
st.components.v1.html(
    f'<div style="background:#d8d8d8;padding:12px;border-radius:8px;overflow-x:auto">{svg_preview}</div>',
    height=svg_height + export_pad + 40,
    scrolling=True
)

# ─── Download buttons ─────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
fname = title_text.replace(' ', '_')

with col_a:
    st.download_button(
        label=T["dl_svg"],
        data=svg_str.encode("utf-8"),
        file_name=f"{fname}_zones.svg",
        mime="image/svg+xml",
        use_container_width=True,
    )

with col_b:
    dxf_bytes = render_dxf(
        elements, svg_w, svg_height, stroke_color,
        dxf_scale=dxf_scale, offset_x=offset_x, offset_y=offset_y,
        plate_w_mm=plate_w_mm, plate_h_mm=plate_h_mm, draw_border=plate_border
    )
    st.download_button(
        label=T["dl_dxf"],
        data=dxf_bytes,
        file_name=f"{fname}_zones.dxf",
        mime="application/dxf",
        use_container_width=True,
    )

st.caption(T["tip"])