import streamlit as st

st.set_page_config(page_title="ARBURG Zone Diagram Generator", layout="wide")

st.title("🔌 ARBURG Zone Diagram Generator")
st.markdown("Configure heating zones and export as SVG.")

# ─── Sidebar config ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ General Settings")
    title_text    = st.text_input("Diagram title", value="ARBURG")
    num_zones     = st.slider("Number of zones", 1, 12, 6)
    zone_width    = st.slider("Zone width (px)", 180, 320, 256)
    svg_height    = st.slider("Diagram height (px)", 400, 800, 580)

    st.markdown("---")
    st.header("📐 Symbol Settings")
    show_polarity   = st.checkbox("Show +/− polarity labels", value=True)
    show_zone_lbl   = st.checkbox("Show zone labels", value=True)
    heater_dividers = st.slider("Heater internal dividers", 0, 5, 3)

    st.markdown("---")
    st.header("🎨 Style")
    stroke_color   = st.color_picker("Line / stroke color",  value="#444444")
    bg_color       = st.color_picker("Background color",     value="#ffffff")
    inactive_color = st.color_picker("Inactive cross color", value="#cc0000")
    font_size_num  = st.slider("Terminal number font size", 14, 36, 24)

# ─── Terminal numbering scheme ────────────────────────────────────────────────
st.subheader("Terminal numbering scheme")
num_scheme = st.radio(
    "Auto-numbering pattern",
    ["Sequential pairs  (1-2, 3-4 … heater;  13-14 … TC)",
     "Custom (enter manually)"],
    horizontal=True
)

# ─── Per-zone configuration ───────────────────────────────────────────────────
st.subheader("Per-zone configuration")

zone_configs = []   # (t1, t2, t3, t4, zone_num, active, wattage_str)

cols_per_row = min(num_zones, 6)
rows_needed  = (num_zones + cols_per_row - 1) // cols_per_row
col_sets     = [st.columns(cols_per_row) for _ in range(rows_needed)]

for z in range(num_zones):
    row   = z // cols_per_row
    col_i = z % cols_per_row
    with col_sets[row][col_i]:
        st.markdown(f"**Zone {z+1}**")

        active  = st.checkbox("Active", value=True, key=f"act{z}")
        wattage = ""
        if active:
            wattage = st.text_input("Wattage", value="350 W", key=f"wat{z}")

        if num_scheme.startswith("Custom"):
            h_top = st.number_input("H+",  value=z*2+1,             key=f"ht{z}", step=1)
            h_bot = st.number_input("H−",  value=z*2+2,             key=f"hb{z}", step=1)
            t_top = st.number_input("TC+", value=z*2+1+num_zones*2, key=f"tt{z}", step=1)
            t_bot = st.number_input("TC−", value=z*2+2+num_zones*2, key=f"tb{z}", step=1)
            zone_configs.append((int(h_top), int(h_bot), int(t_top), int(t_bot),
                                  z+1, active, wattage))
        else:
            zone_configs.append((
                z*2 + 1,          z*2 + 2,
                z*2 + 1 + num_zones*2, z*2 + 2 + num_zones*2,
                z+1, active, wattage
            ))

# ─── SVG generation ───────────────────────────────────────────────────────────
def generate_svg(zones, title, zone_w, svg_h,
                 stroke, bg, inactive_col, font_num,
                 show_pol, show_zlbl, dividers):

    num_z = len(zones)
    svg_w = zone_w * num_z + 4

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

    L = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {svg_w} {svg_h}" '
             f'width="{svg_w}" height="{svg_h}" '
             f'style="background:{bg}">')

    L.append(f'''<defs><style>
  .terminal {{ fill:{bg}; stroke:{stroke}; stroke-width:1.8; }}
  .num  {{ font-family:Arial,sans-serif; font-size:{font_num}px; fill:{stroke};
            text-anchor:middle; dominant-baseline:central; }}
  .title {{ font-family:Arial,sans-serif; font-size:{int(svg_h*0.076)}px; fill:{stroke};
             text-anchor:middle; dominant-baseline:central; letter-spacing:10px; font-weight:300; }}
  .zlbl {{ font-family:Arial,sans-serif; font-size:{int(svg_h*0.029)}px; fill:{stroke};
            text-anchor:middle; letter-spacing:2px; }}
  .pwrl {{ font-family:Arial,sans-serif; font-size:{int(svg_h*0.029)}px; fill:{stroke};
            text-anchor:middle; }}
  .pol  {{ font-family:Arial,sans-serif; font-size:{int(svg_h*0.033)}px; fill:{stroke};
            dominant-baseline:central; }}
  line, polyline {{ stroke:{stroke}; fill:none; stroke-width:1.8; }}
  rect.heater {{ fill:{bg}; stroke:{stroke}; stroke-width:1.8; }}
  circle.junc {{ fill:{bg}; stroke:{stroke}; stroke-width:1.8; }}
  .cross {{ stroke:{inactive_col}; stroke-width:4; stroke-linecap:round; opacity:0.85; }}
</style></defs>''')

    # Title
    L.append(f'<text x="{svg_w//2}" y="{int(svg_h*0.048)}" class="title">{title}</text>')

    for i, (t1, t2, t3, t4, zn, active, wattage) in enumerate(zones):
        ox = i * zone_w + 2
        hx = ox + H_CX
        tx = ox + T_CX

        # Zone separator
        if i > 0:
            L.append(f'<line x1="{ox-2}" y1="0" x2="{ox-2}" y2="{svg_h}" '
                     f'stroke="{stroke}" stroke-width="1.5"/>')

        # ── Heater ──
        L.append(f'<circle cx="{hx}" cy="{TOP_Y}" r="{CR}" class="terminal"/>')
        L.append(f'<text x="{hx}" y="{TOP_Y}" class="num">{t1}</text>')
        L.append(f'<line x1="{hx}" y1="{TOP_Y+CR}" x2="{hx}" y2="{HR_TOP}"/>')
        L.append(f'<rect x="{ox+HR_X}" y="{HR_TOP}" width="{HR_W}" height="{HR_H}" class="heater"/>')
        if dividers > 0:
            step = HR_H / (dividers + 1)
            for d in range(1, dividers + 1):
                dy = int(HR_TOP + step * d)
                L.append(f'<line x1="{ox+HR_X+4}" y1="{dy}" x2="{ox+HR_X+HR_W-4}" y2="{dy}"/>')
        if show_pol:
            L.append(f'<text x="{hx+CR-4}" y="{HR_TOP+HR_H+int(svg_h*0.038)}" class="pol">-</text>')
        L.append(f'<line x1="{hx}" y1="{HR_TOP+HR_H}" x2="{hx}" y2="{BOT_Y-CR}"/>')
        L.append(f'<circle cx="{hx}" cy="{BOT_Y}" r="{CR}" class="terminal"/>')
        L.append(f'<text x="{hx}" y="{BOT_Y}" class="num">{t2}</text>')

        # ── Thermocouple ──
        L.append(f'<circle cx="{tx}" cy="{TOP_Y}" r="{CR}" class="terminal"/>')
        L.append(f'<text x="{tx}" y="{TOP_Y}" class="num">{t3}</text>')
        if show_pol:
            L.append(f'<text x="{tx+CR//2}" y="{int(svg_h*0.270)}" class="pol">+</text>')
        L.append(f'<line x1="{tx}" y1="{TOP_Y+CR}" x2="{tx}" y2="{chevron_top}"/>')
        tip_x = tx + tip_dx
        L.append(f'<polyline points="{tx},{chevron_top} {tip_x},{junc_y}"/>')
        L.append(f'<circle cx="{tip_x}" cy="{junc_y}" r="{max(5,int(zone_w*0.027))}" class="junc"/>')
        L.append(f'<polyline points="{tip_x},{junc_y} {tx},{chevron_bot}"/>')
        L.append(f'<line x1="{tx}" y1="{chevron_bot}" x2="{tx}" y2="{BOT_Y-CR}"/>')
        if show_pol:
            L.append(f'<text x="{tx+CR//2}" y="{int(svg_h*0.724)}" class="pol">-</text>')
        L.append(f'<circle cx="{tx}" cy="{BOT_Y}" r="{CR}" class="terminal"/>')
        L.append(f'<text x="{tx}" y="{BOT_Y}" class="num">{t4}</text>')

        mid_x = ox + (H_CX + T_CX) // 2

        # ── Active: show wattage  |  Inactive: red X ──
        if active:
            if wattage.strip():
                L.append(f'<text x="{mid_x}" y="{int(svg_h*0.786)}" class="pwrl">{wattage}</text>')
        else:
            x0 = ox + CROSS_PAD_X
            x1 = ox + zone_w - CROSS_PAD_X
            L.append(f'<line x1="{x0}" y1="{CROSS_TOP}" x2="{x1}" y2="{CROSS_BOT}" class="cross"/>')
            L.append(f'<line x1="{x1}" y1="{CROSS_TOP}" x2="{x0}" y2="{CROSS_BOT}" class="cross"/>')

        if show_zlbl:
            L.append(f'<text x="{mid_x}" y="{int(svg_h*0.940)}" class="zlbl">ZONE {zn}</text>')

    L.append('</svg>')
    return '\n'.join(L)


# ─── Preview & download ───────────────────────────────────────────────────────
svg_str = generate_svg(
    zone_configs, title_text, zone_width, svg_height,
    stroke_color, bg_color, inactive_color, font_size_num,
    show_polarity, show_zone_lbl, heater_dividers
)

st.markdown("---")
st.subheader("Preview")
st.components.v1.html(
    f'<div style="overflow-x:auto;background:#e0e0e0;padding:12px;border-radius:8px">'
    f'{svg_str}</div>',
    height=svg_height + 40,
    scrolling=True
)

st.download_button(
    label="⬇️  Download SVG",
    data=svg_str.encode("utf-8"),
    file_name=f"{title_text.replace(' ','_')}_zones.svg",
    mime="image/svg+xml",
    use_container_width=True,
)

st.caption("Tip: open the downloaded SVG in Inkscape or a browser for further editing.")
