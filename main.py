import streamlit as st
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath

# ─── Text → SVG path helper ───────────────────────────────────────────────────
def tp(text, cx, cy, font_size, anchor='middle', fill='#444444'):
    """Convert a string to an SVG <path> element (no <text> tags)."""
    if not text:
        return ''
    fp = FontProperties(family='DejaVu Sans')
    mtp = TextPath((0, 0), text, size=font_size, prop=fp)
    bb  = mtp.get_extents()
    tw  = bb.x1 - bb.x0

    if anchor == 'middle':
        ox = cx - tw / 2 - bb.x0
    elif anchor == 'end':
        ox = cx - tw - bb.x0
    else:
        ox = cx - bb.x0

    # Vertical: centre of glyph bounding box → cy
    text_mid_y = (bb.y0 + bb.y1) / 2
    oy = cy + text_mid_y          # SVG y = oy − matplotlib y

    verts = mtp.vertices
    codes = mtp.codes
    d = []
    i = 0
    n = len(codes)
    while i < n:
        code = codes[i]
        vx, vy = verts[i]
        sx = vx + ox;  sy = oy - vy
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
            vx2, vy2 = verts[i+1];  vx3, vy3 = verts[i+2]
            d.append(f'C {sx:.2f},{sy:.2f} {vx2+ox:.2f},{oy-vy2:.2f} {vx3+ox:.2f},{oy-vy3:.2f}')
            i += 3
        elif code == MplPath.CLOSEPOLY:
            d.append('Z')
            i += 1
        else:
            i += 1
    return f'<path d="{" ".join(d)}" fill="{fill}" stroke="none"/>'


# ─── Language packages ────────────────────────────────────────────────────────
LANG = {
    "SL": {
        "app_title":     "🔌 Generator sheme con ARBURG",
        "app_sub":       "Konfigurirajte grelne cone in izvozite SVG.",
        "general":       "⚙️ Splošne nastavitve",
        "diag_title":    "Naziv diagrama",
        "num_zones":     "Število con",
        "zone_width":    "Širina cone (px)",
        "svg_height":    "Višina diagrama (px)",
        "symbol":        "📐 Nastavitve simbolov",
        "show_pol":      "Prikaži oznake +/−",
        "show_zlbl":     "Prikaži oznake con",
        "dividers":      "Notranje črte grelca",
        "style":         "🎨 Slog",
        "stroke_col":    "Barva linij",
        "bg_col":        "Barva ozadja",
        "inact_col":     "Barva križa (neaktivno)",
        "font_sz":       "Velikost pisave terminalov",
        "num_scheme":    "Shema številčenja terminalov",
        "seq_label":     "Zaporedno (1-2, 3-4 … grelec; 13-14 … TC)",
        "custom_label":  "Po meri (ročni vnos)",
        "per_zone":      "Konfiguracija po conah",
        "zone_hdr":      "Cona",
        "active_lbl":    "Aktivna",
        "wattage_lbl":   "Moč",
        "wattage_def":   "350 W",
        "zone_type_lbl": "Tip cone",
        "type_nozzle":   "VSTOPNA SOBA",   # without Š for laser compat
        "type_block":    "GRELNI BLOK",
        "type_heater":   "GRELEC",
        "warn_nozzle":   "⚠️ VSTOPNA ŠOBA je že dodeljena coni {z}. Samo ena je dovoljena.",
        "warn_block":    "⚠️ GRELNI BLOK je že dodeljen coni {z}. Samo eden je dovoljen.",
        "h_plus":        "G+",
        "h_minus":       "G−",
        "tc_plus":       "TC+",
        "tc_minus":      "TC−",
        "preview":       "Predogled",
        "download":      "⬇️  Prenesi SVG",
        "tip":           "Nasvet: odprite SVG v Inkscape ali brskalniku za urejanje.",
        "type_nozzle_svg": "VSTOPNA SOBA",
        "type_block_svg":  "GRELNI BLOK",
        "type_heater_svg": "GRELEC",
    },
    "EN": {
        "app_title":     "🔌 ARBURG Zone Diagram Generator",
        "app_sub":       "Configure heating zones and export as SVG.",
        "general":       "⚙️ General Settings",
        "diag_title":    "Diagram title",
        "num_zones":     "Number of zones",
        "zone_width":    "Zone width (px)",
        "svg_height":    "Diagram height (px)",
        "symbol":        "📐 Symbol Settings",
        "show_pol":      "Show +/− polarity labels",
        "show_zlbl":     "Show zone labels",
        "dividers":      "Heater internal dividers",
        "style":         "🎨 Style",
        "stroke_col":    "Line / stroke color",
        "bg_col":        "Background color",
        "inact_col":     "Inactive cross color",
        "font_sz":       "Terminal number font size",
        "num_scheme":    "Terminal numbering scheme",
        "seq_label":     "Sequential pairs (1-2, 3-4 … heater; 13-14 … TC)",
        "custom_label":  "Custom (enter manually)",
        "per_zone":      "Per-zone configuration",
        "zone_hdr":      "Zone",
        "active_lbl":    "Active",
        "wattage_lbl":   "Wattage",
        "wattage_def":   "350 W",
        "zone_type_lbl": "Zone type",
        "type_nozzle":   "NOZZLE",
        "type_block":    "HEATING BLOCK",
        "type_heater":   "HEATER",
        "warn_nozzle":   "⚠️ NOZZLE already assigned to zone {z}. Only one allowed.",
        "warn_block":    "⚠️ HEATING BLOCK already assigned to zone {z}. Only one allowed.",
        "h_plus":        "H+",
        "h_minus":       "H−",
        "tc_plus":       "TC+",
        "tc_minus":      "TC−",
        "preview":       "Preview",
        "download":      "⬇️  Download SVG",
        "tip":           "Tip: open the SVG in Inkscape or a browser for further editing.",
        "type_nozzle_svg": "NOZZLE",
        "type_block_svg":  "HEATING BLOCK",
        "type_heater_svg": "HEATER",
    },
}

# ─── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ARBURG Zone Diagram Generator", layout="wide")

with st.sidebar:
    lang_choice = st.selectbox("🌐 Jezik / Language", ["SL", "EN"], index=0)

T = LANG[lang_choice]

st.title(T["app_title"])
st.markdown(T["app_sub"])

# ─── Sidebar config ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header(T["general"])
    title_text      = st.text_input(T["diag_title"], value="ARBURG")
    num_zones       = st.slider(T["num_zones"], 1, 12, 6)
    zone_width      = st.slider(T["zone_width"], 180, 320, 256)
    svg_height      = st.slider(T["svg_height"], 400, 800, 580)

    st.markdown("---")
    st.header(T["symbol"])
    show_polarity   = st.checkbox(T["show_pol"], value=True)
    show_zone_lbl   = st.checkbox(T["show_zlbl"], value=True)
    heater_dividers = st.slider(T["dividers"], 0, 5, 3)

    st.markdown("---")
    st.header(T["style"])
    stroke_color    = st.color_picker(T["stroke_col"],  value="#444444")
    bg_color        = st.color_picker(T["bg_col"],      value="#ffffff")
    inactive_color  = st.color_picker(T["inact_col"],   value="#cc0000")
    font_size_num   = st.slider(T["font_sz"], 14, 36, 24)

# ─── Terminal numbering scheme ────────────────────────────────────────────────
st.subheader(T["num_scheme"])
num_scheme = st.radio("", [T["seq_label"], T["custom_label"]],
                      horizontal=True, label_visibility="collapsed")

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
    row = z // cols_per_row
    col_i = z % cols_per_row
    with col_sets[row][col_i]:
        st.markdown(f"**{T['zone_hdr']} {z+1}**")

        zone_type = st.selectbox(T["zone_type_lbl"], ZONE_TYPES,
                                 index=2, key=f"ztype{z}")

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
            svg_label = T["type_nozzle_svg"]
        elif zone_type == T["type_block"]:
            svg_label = T["type_block_svg"]
        else:
            heater_counter += 1
            svg_label = f"{T['type_heater_svg']} {heater_counter}"

        active  = st.checkbox(T["active_lbl"], value=True, key=f"act{z}")
        wattage = ""
        if active:
            wattage = st.text_input(T["wattage_lbl"], value=T["wattage_def"], key=f"wat{z}")

        if num_scheme == T["custom_label"]:
            h_top = st.number_input(T["h_plus"],  value=z*2+1,             key=f"ht{z}", step=1)
            h_bot = st.number_input(T["h_minus"], value=z*2+2,             key=f"hb{z}", step=1)
            t_top = st.number_input(T["tc_plus"], value=z*2+1+num_zones*2, key=f"tt{z}", step=1)
            t_bot = st.number_input(T["tc_minus"],value=z*2+2+num_zones*2, key=f"tb{z}", step=1)
            zone_configs.append((int(h_top), int(h_bot), int(t_top), int(t_bot),
                                  svg_label, active, wattage))
        else:
            zone_configs.append((
                z*2+1, z*2+2,
                z*2+1+num_zones*2, z*2+2+num_zones*2,
                svg_label, active, wattage
            ))


# ─── SVG generation (no <text> — all paths) ──────────────────────────────────
def generate_svg(zones, title, zone_w, svg_h,
                 stroke, bg, inactive_col, font_num,
                 show_pol, show_zlbl, dividers):

    svg_w = zone_w * len(zones) + 4

    H_CX  = zone_w * 30 // 100
    T_CX  = zone_w * 70 // 100
    TOP_Y = int(svg_h * 0.145)
    BOT_Y = int(svg_h * 0.852)
    CR    = int(zone_w * 0.125)

    HR_TOP = int(svg_h * 0.232)
    HR_H   = int(svg_h * 0.483)
    HR_W   = int(zone_w * 0.226)
    HR_X   = H_CX - HR_W // 2

    chevron_top = int(svg_h * 0.396)
    chevron_bot = int(svg_h * 0.672)
    junc_y      = (chevron_top + chevron_bot) // 2
    tip_dx      = int(zone_w * 0.109)

    CROSS_PAD_X = int(zone_w * 0.06)
    CROSS_TOP   = int(svg_h * 0.10)
    CROSS_BOT   = int(svg_h * 0.90)

    fs_num   = font_num
    fs_title = int(svg_h * 0.076)
    fs_lbl   = int(svg_h * 0.029)
    fs_pol   = int(svg_h * 0.033)

    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {svg_w} {svg_h}" '
             f'width="{svg_w}" height="{svg_h}" '
             f'style="background:{bg}">')
    L.append(f'<defs><style>'
             f'line,polyline{{stroke:{stroke};fill:none;stroke-width:1.8;}}'
             f'rect.heater{{fill:{bg};stroke:{stroke};stroke-width:1.8;}}'
             f'circle.terminal{{fill:{bg};stroke:{stroke};stroke-width:1.8;}}'
             f'circle.junc{{fill:{bg};stroke:{stroke};stroke-width:1.8;}}'
             f'.cross{{stroke:{inactive_col};stroke-width:4;stroke-linecap:round;opacity:0.85;}}'
             f'</style></defs>')

    # Title — path
    L.append(tp(title, svg_w // 2, int(svg_h * 0.048), fs_title, 'middle', stroke))

    for i, (t1, t2, t3, t4, zlabel, active, wattage) in enumerate(zones):
        ox  = i * zone_w + 2
        hx  = ox + H_CX
        tx  = ox + T_CX
        mid = ox + (H_CX + T_CX) // 2

        # Separator
        if i > 0:
            L.append(f'<line x1="{ox-2}" y1="0" x2="{ox-2}" y2="{svg_h}" '
                     f'stroke="{stroke}" stroke-width="1.5"/>')

        # ── Heater ──
        L.append(f'<circle cx="{hx}" cy="{TOP_Y}" r="{CR}" class="terminal"/>')
        L.append(tp(str(t1), hx, TOP_Y, fs_num, 'middle', stroke))
        L.append(f'<line x1="{hx}" y1="{TOP_Y+CR}" x2="{hx}" y2="{HR_TOP}"/>')
        L.append(f'<rect x="{ox+HR_X}" y="{HR_TOP}" width="{HR_W}" height="{HR_H}" class="heater"/>')
        if dividers > 0:
            step = HR_H / (dividers + 1)
            for d in range(1, dividers + 1):
                dy = int(HR_TOP + step * d)
                L.append(f'<line x1="{ox+HR_X+4}" y1="{dy}" x2="{ox+HR_X+HR_W-4}" y2="{dy}"/>')
        L.append(f'<line x1="{hx}" y1="{HR_TOP+HR_H}" x2="{hx}" y2="{BOT_Y-CR}"/>')
        L.append(f'<circle cx="{hx}" cy="{BOT_Y}" r="{CR}" class="terminal"/>')
        L.append(tp(str(t2), hx, BOT_Y, fs_num, 'middle', stroke))

        # ── Thermocouple ──
        L.append(f'<circle cx="{tx}" cy="{TOP_Y}" r="{CR}" class="terminal"/>')
        L.append(tp(str(t3), tx, TOP_Y, fs_num, 'middle', stroke))
        if show_pol:
            L.append(tp('+', tx + CR // 2 + fs_pol // 2, int(svg_h * 0.270), fs_pol, 'start', stroke))
        L.append(f'<line x1="{tx}" y1="{TOP_Y+CR}" x2="{tx}" y2="{chevron_top}"/>')
        tip_x = tx + tip_dx
        L.append(f'<polyline points="{tx},{chevron_top} {tip_x},{junc_y}"/>')
        L.append(f'<circle cx="{tip_x}" cy="{junc_y}" r="{max(5,int(zone_w*0.027))}" class="junc"/>')
        L.append(f'<polyline points="{tip_x},{junc_y} {tx},{chevron_bot}"/>')
        L.append(f'<line x1="{tx}" y1="{chevron_bot}" x2="{tx}" y2="{BOT_Y-CR}"/>')
        if show_pol:
            L.append(tp('-', tx + CR // 2 + fs_pol // 2, int(svg_h * 0.724), fs_pol, 'start', stroke))
        L.append(f'<circle cx="{tx}" cy="{BOT_Y}" r="{CR}" class="terminal"/>')
        L.append(tp(str(t4), tx, BOT_Y, fs_num, 'middle', stroke))

        # ── Inactive cross ──
        if not active:
            x0 = ox + CROSS_PAD_X
            x1 = ox + zone_w - CROSS_PAD_X
            L.append(f'<line x1="{x0}" y1="{CROSS_TOP}" x2="{x1}" y2="{CROSS_BOT}" class="cross"/>')
            L.append(f'<line x1="{x1}" y1="{CROSS_TOP}" x2="{x0}" y2="{CROSS_BOT}" class="cross"/>')

        # ── Zone label + wattage (only when active) ──
        if show_zlbl and active:
            L.append(tp(zlabel, mid, int(svg_h * 0.950), fs_lbl, 'middle', stroke))
        if active and wattage.strip():
            L.append(tp(wattage, mid, int(svg_h * 0.985), fs_lbl, 'middle', stroke))

    L.append('</svg>')
    return '\n'.join(L)


# ─── Preview & download ───────────────────────────────────────────────────────
svg_str = generate_svg(
    zone_configs, title_text, zone_width, svg_height,
    stroke_color, bg_color, inactive_color, font_size_num,
    show_polarity, show_zone_lbl, heater_dividers
)

st.markdown("---")
st.subheader(T["preview"])
st.components.v1.html(
    f'<div style="overflow-x:auto;background:#e0e0e0;padding:12px;border-radius:8px">'
    f'{svg_str}</div>',
    height=svg_height + 40,
    scrolling=True
)

st.download_button(
    label=T["download"],
    data=svg_str.encode("utf-8"),
    file_name=f"{title_text.replace(' ','_')}_zones.svg",
    mime="image/svg+xml",
    use_container_width=True,
)

st.caption(T["tip"])
