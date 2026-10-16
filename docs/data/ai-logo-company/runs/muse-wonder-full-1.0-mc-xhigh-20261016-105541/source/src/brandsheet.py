#!/usr/bin/env python3
"""Brand sheet, app icon, and animation-frame SVGs for Morpha."""
import sys, math
sys.path.insert(0, "src")
from logo import *

X0, Y0, X1, Y1 = mark_bbox()
MW, MH = X1 - X0, Y1 - Y0
FONT = "Avenir Next,Helvetica Neue,Helvetica,Arial,sans-serif"
MONO = "SF Mono,Menlo,Consolas,monospace"
LINE = "#DED4C2"
CARD = "#FFFFFF"

def g_mark(x, y, h, ink=INK, mid=MID, pale=CLAY, **kw):
    """Mark with its bbox top-left at (x, y), height h. Returns (svg, width)."""
    s = h / MH
    svg = (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f}) '
           f'translate({-X0:.1f},{-Y0:.1f})">{mark(ink, mid, pale, **kw)}</g>')
    return svg, MW * s

def g_word(x, y_base, s, col=INK):
    wm, _, _ = wordmark(col=col)
    return f'<g transform="translate({x:.1f},{y_base - B * s:.1f}) scale({s:.4f})">{wm}</g>'

def lockup(x, y, mark_h, ink=INK, mid=MID, pale=CLAY, wm_col=None):
    """Horizontal lockup, mark bbox top-left at (x,y). Returns (svg, total_w)."""
    wm_col = wm_col or ink
    s = mark_h / MH
    m_svg, m_w = g_mark(x, y, mark_h, ink, mid, pale)
    ws = s * (MH * 0.34) / XHEIGHT
    gap = MH * 0.22 * s
    wx = x + m_w + gap
    wbase = y + mark_h / 2 + (B - (T + B) / 2) * ws
    return m_svg + g_word(wx, wbase, ws, wm_col), m_w + gap + WM_W * ws

def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")

def label(x, y, text, col=GREY, size=25, anchor="start", ls=4, weight=500):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" letter-spacing="{ls}" fill="{col}">{_esc(text)}</text>')

def body_text(x, y, text, col=GREY, size=28, anchor="start", weight=400, ls=0):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" letter-spacing="{ls}" fill="{col}">{_esc(text)}</text>')

def construction(x, y, h):
    s = h / MH
    guides = []
    for (cx, cy, r, _, _) in (MAIN, BUD, SPORE):
        guides.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{STONE}" '
                      f'stroke-width="1.6" stroke-dasharray="7 7"/>')
        guides.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{STONE}"/>')
    axis = (f'<line x1="{MAIN[0]-55}" y1="{MAIN[1]+52}" x2="{SPORE[0]+34}" y2="{SPORE[1]-32}" '
            f'stroke="{CLAY}" stroke-width="1.6" stroke-dasharray="2 8" stroke-linecap="round"/>')
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f}) translate({-X0:.1f},{-Y0:.1f})">'
            + axis + mark() + "".join(guides) + "</g>", MW * s)

PALETTE = [("Ink", INK), ("Warm grey", MID), ("Stone", STONE),
           ("Clay", CLAY), ("Sand", SAND), ("Bone", BONE)]

def sheet_svg():
    W, H = 2400, 1680
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{BONE}"/>']
    # header
    p.append(label(120, 118, "MORPHA — IDENTITY", INK, 30, ls=6))
    p.append(label(2280, 118, "LOGO SHEET · V1", GREY, 24, anchor="end", ls=4, weight=400))
    p.append(f'<line x1="120" y1="152" x2="2280" y2="152" stroke="{LINE}" stroke-width="2"/>')
    # Panel A: primary
    p.append(f'<rect x="120" y="190" width="2160" height="470" fill="{CARD}" stroke="{LINE}"/>')
    svg_lk, w_lk = lockup(0, 0, 300)
    p.append(f'<g transform="translate({(W - w_lk) / 2:.0f},275)">{svg_lk}</g>')
    p.append(label(170, 612, "01 — PRIMARY LOCKUP"))
    p.append(body_text(2230, 612, "custom monoline wordmark", GREY, 25, anchor="end"))
    # Panel B: reversed
    p.append(f'<rect x="120" y="700" width="1060" height="420" fill="{INK}"/>')
    svg_rv, w_rv = lockup(0, 0, 205, BONE, CLAY, STONE, wm_col=BONE)
    p.append(f'<g transform="translate({120 + (1060 - w_rv) / 2:.0f},807)">{svg_rv}</g>')
    p.append(label(170, 1072, "02 — REVERSED", col=CLAY))
    # Panel C: construction
    p.append(f'<rect x="1220" y="700" width="1060" height="420" fill="{CARD}" stroke="{LINE}"/>')
    svg_c, w_c = construction(1310, 775, 265)
    p.append(svg_c)
    tx = 1760
    rows = [("Parent stone", "seed A · growth-ring crescent", INK),
            ("Bud", "seed B · new generation", MID),
            ("Spore", "seed C · released variant", CLAY)]
    for i, (name, note, col) in enumerate(rows):
        yy = 812 + i * 72
        p.append(f'<circle cx="{tx}" cy="{yy - 9}" r="11" fill="{col}"/>')
        p.append(body_text(tx + 32, yy, name, INK, 29, weight=500))
        p.append(body_text(tx + 32, yy + 30, note, GREY, 24))
    p.append(body_text(tx, 1046, "One harmonic pebble function,", GREY, 26))
    p.append(body_text(tx, 1080, "re-seeded — generation as geometry.", GREY, 26))
    p.append(label(1270, 1072, "03 — CONSTRUCTION"))
    # Panel D: palette
    p.append(f'<rect x="120" y="1160" width="700" height="400" fill="{CARD}" stroke="{LINE}"/>')
    p.append(label(170, 1218, "04 — PALETTE"))
    for i, (name, hexv) in enumerate(PALETTE):
        yy = 1242 + i * 50
        stroke = ' stroke="#CFC4AE"' if hexv in (BONE, SAND) else ""
        p.append(f'<rect x="170" y="{yy}" width="210" height="38" fill="{hexv}"{stroke}/>')
        p.append(body_text(404, yy + 27, name, INK, 26))
        p.append(f'<text x="770" y="{yy + 27}" text-anchor="end" font-family="{MONO}" '
                 f'font-size="24" fill="{GREY}">{hexv}</text>')
    # Panel E: variations
    p.append(f'<rect x="860" y="1160" width="760" height="400" fill="{CARD}" stroke="{LINE}"/>')
    p.append(label(910, 1218, "05 — VARIATIONS"))
    svg_mono, w_mono = lockup(0, 0, 104, INK, INK, INK)
    p.append(f'<g transform="translate(915,1248)">{svg_mono}</g>')
    p.append(body_text(915, 1392, "One-colour", GREY, 24))
    p.append(f'<line x1="910" y1="1414" x2="1570" y2="1414" stroke="{LINE}" stroke-width="2"/>')
    svg_mk, w_mk = g_mark(915, 1432, 104)
    p.append(svg_mk)
    p.append(body_text(915 + w_mk + 40, 1492, "Mark only — social avatar, favicon", GREY, 24))
    # Panel F: clearspace & scale & app icon
    p.append(f'<rect x="1660" y="1160" width="620" height="400" fill="{CARD}" stroke="{LINE}"/>')
    p.append(label(1710, 1218, "06 — CLEARSPACE & SCALE"))
    cs_h = 116; s = cs_h / MH; xu = 24 * s          # x = spore diameter
    cx0, cy0 = 1742, 1272
    svg_cs, w_cs = g_mark(cx0, cy0, cs_h)
    p.append(f'<rect x="{cx0 - xu:.0f}" y="{cy0 - xu:.0f}" width="{w_cs + 2 * xu:.0f}" '
             f'height="{cs_h + 2 * xu:.0f}" fill="none" stroke="{STONE}" stroke-width="1.6" stroke-dasharray="7 7"/>')
    p.append(svg_cs)
    p.append(body_text(cx0 - xu + 3, cy0 - 5, "x", STONE, 22, weight=500))
    p.append(body_text(cx0 - xu, cy0 + cs_h + xu + 34, "x = spore diameter", GREY, 24))
    # app icon (mini)
    ax, ay, asz = 2075, 1256, 150
    p.append(f'<rect x="{ax}" y="{ay}" width="{asz}" height="{asz}" rx="34" fill="{INK}"/>')
    ah = asz * 0.52
    svg_ai, w_ai = g_mark(ax + (asz - (MW * ah / MH)) / 2, ay + (asz - ah) / 2, ah, BONE, CLAY, STONE)
    p.append(svg_ai)
    p.append(body_text(ax + asz / 2, ay + asz + 34, "App icon", GREY, 24, anchor="middle"))
    # scale row
    sy = 1486
    xx = 1712
    for px in (64, 32, 16):
        svg_s, w_s = g_mark(xx, sy - px + 64, px)
        p.append(svg_s)
        p.append(body_text(xx + w_s / 2, sy + 92, f"{px}", GREY, 22, anchor="middle"))
        xx += w_s + 56
    p.append(body_text(xx - 40, sy + 92, "px", GREY, 22))
    # footer
    p.append(f'<line x1="120" y1="1606" x2="2280" y2="1606" stroke="{LINE}" stroke-width="2"/>')
    p.append(body_text(120, 1648, "Grown, not built — a generative-AI identity in warm neutrals.", GREY, 26))
    p.append(label(2280, 1648, "MORPHA", INK, 24, anchor="end", ls=5))
    p.append("</svg>")
    return "\n".join(p)

def appicon_svg():
    S = 1024
    h = S * 0.54
    svg_m, w_m = g_mark((S - MW * h / MH) / 2, (S - h) / 2, h, BONE, CLAY, STONE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">'
            f'<rect width="{S}" height="{S}" rx="232" fill="{INK}"/>{svg_m}</svg>\n')

def frame_svg(t):
    """t in [0,1): one seamless morph cycle."""
    S = 720
    morph = 0.55 * math.sin(2 * math.pi * t)
    bud_shift = 2.4 * math.sin(2 * math.pi * t + 0.7)
    spore_r = 12 + 1.8 * math.sin(2 * math.pi * t + 1.9)
    h = 320
    svg_m, w_m = g_mark((S - MW * h / MH) / 2, 108, h,
                        morph=morph, bud_shift=bud_shift, spore_r=spore_r)
    ws = 372 / WM_W
    word = g_word((S - WM_W * ws) / 2, 596, ws, INK)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">'
            f'<rect width="{S}" height="{S}" fill="{BONE}"/>{svg_m}{word}</svg>\n')

if __name__ == "__main__":
    open("/tmp/sheet.svg", "w").write(sheet_svg())
    open("/tmp/appicon.svg", "w").write(appicon_svg())
    open("/tmp/frame0.svg", "w").write(frame_svg(0.0))
    print("ok")
