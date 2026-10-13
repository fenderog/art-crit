#!/usr/bin/env python3
"""Awkward robot family portrait — SVG generator. No text in output."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "output" / "awkward-robot-family.svg"

P = []
def add(s):
    P.append(s)

add('<?xml version="1.0" encoding="UTF-8"?>')
add('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">')
add('<defs>')
add('<linearGradient id="backdrop" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#4a3e36"/>'
    '<stop offset="0.45" stop-color="#9a8268"/>'
    '<stop offset="0.62" stop-color="#d9c19c"/>'
    '<stop offset="0.76" stop-color="#a68d6d"/>'
    '<stop offset="1" stop-color="#5a4c3e"/></linearGradient>')
add('<radialGradient id="glow" cx="0.5" cy="0.42" r="0.55">'
    '<stop offset="0" stop-color="#f5e6c8" stop-opacity="0.85"/>'
    '<stop offset="0.6" stop-color="#e8d0a5" stop-opacity="0.35"/>'
    '<stop offset="1" stop-color="#e8d0a5" stop-opacity="0"/></radialGradient>')
add('<linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#8a7057"/><stop offset="1" stop-color="#453626"/></linearGradient>')
add('<linearGradient id="curtainG" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#3a0f11"/><stop offset="0.5" stop-color="#8a2f33"/>'
    '<stop offset="1" stop-color="#3a0f11"/></linearGradient>')
add('<linearGradient id="dadMetal" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#4a5058"/><stop offset="0.5" stop-color="#8b939d"/>'
    '<stop offset="1" stop-color="#525860"/></linearGradient>')
add('<linearGradient id="dadHead" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#9aa2ac"/><stop offset="1" stop-color="#5c636c"/></linearGradient>')
add('<linearGradient id="momBody" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#7fb89e"/><stop offset="0.5" stop-color="#d4efe0"/>'
    '<stop offset="1" stop-color="#6da88d"/></linearGradient>')
add('<linearGradient id="teenBody" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#6f5f9e"/><stop offset="0.5" stop-color="#b9aad9"/>'
    '<stop offset="1" stop-color="#665695"/></linearGradient>')
add('<linearGradient id="kidBody" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#c66a12"/><stop offset="0.5" stop-color="#ffc06a"/>'
    '<stop offset="1" stop-color="#c66a12"/></linearGradient>')
add('<linearGradient id="dogBody" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#b9c1c9"/><stop offset="1" stop-color="#7c8791"/></linearGradient>')
add('<radialGradient id="glassShine" cx="0.35" cy="0.3" r="0.8">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/>'
    '<stop offset="0.25" stop-color="#dff3ff" stop-opacity="0.35"/>'
    '<stop offset="1" stop-color="#9fc4d8" stop-opacity="0.15"/></radialGradient>')
add('<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">'
    '<feGaussianBlur stdDeviation="6"/></filter>')
add('<filter id="soft2" x="-40%" y="-40%" width="180%" height="180%">'
    '<feGaussianBlur stdDeviation="2.5"/></filter>')
add('</defs>')
# ---- studio backdrop ----
add('<rect x="0" y="0" width="1200" height="900" fill="url(#backdrop)"/>')
add('<ellipse cx="600" cy="400" rx="520" ry="360" fill="url(#glow)"/>')
# curtains
add('<g>')
add('<path d="M0,0 L150,0 C130,150 140,400 90,680 L0,680 Z" fill="url(#curtainG)"/>')
add('<path d="M30,0 C25,180 35,420 15,660" stroke="#2a0a0b" stroke-width="10" fill="none" opacity="0.6"/>')
add('<path d="M80,0 C70,200 85,430 60,660" stroke="#c86a6a" stroke-width="6" fill="none" opacity="0.35"/>')
add('<path d="M1200,0 L1050,0 C1070,150 1060,400 1110,680 L1200,680 Z" fill="url(#curtainG)"/>')
add('<path d="M1170,0 C1175,180 1165,420 1185,660" stroke="#2a0a0b" stroke-width="10" fill="none" opacity="0.6"/>')
add('<path d="M1120,0 C1130,200 1115,430 1140,660" stroke="#c86a6a" stroke-width="6" fill="none" opacity="0.35"/>')
add('<rect x="0" y="0" width="1200" height="26" fill="#2e2520"/>')
add('<rect x="0" y="26" width="1200" height="8" fill="#c9a86a" opacity="0.7"/>')
add('</g>')
# crooked ancestor frame (tilted)
add('<g transform="translate(928,150) rotate(5)">')
add('<rect x="-90" y="-110" width="180" height="220" rx="8" fill="#3a2c1c"/>')
add('<rect x="-80" y="-100" width="160" height="200" fill="#d9c9a8"/>')
add('<rect x="-68" y="-88" width="136" height="176" fill="#4a4238"/>')
add('<circle cx="0" cy="-30" r="34" fill="#8b939d"/>')
add('<rect x="-26" y="6" width="52" height="60" rx="8" fill="#8b939d"/>')
add('<rect x="-20" y="-38" width="40" height="10" rx="5" fill="#ffcf4d" opacity="0.9"/>')
add('<circle cx="0" cy="-30" r="34" fill="none" stroke="#2e2a24" stroke-width="4" opacity="0.5"/>')
add('</g>')
# backdrop stand leg (visible, awkward)
add('<g opacity="0.9">')
add('<rect x="1162" y="34" width="10" height="650" fill="#222"/>')
add('<rect x="1120" y="668" width="100" height="14" rx="7" fill="#222"/>')
add('<circle cx="1167" cy="60" r="6" fill="#555"/>')
add('</g>')
# floor + carpet
add('<rect x="0" y="678" width="1200" height="222" fill="url(#floorG)"/>')
add('<rect x="0" y="676" width="1200" height="6" fill="#2e2318"/>')
add('<ellipse cx="600" cy="806" rx="440" ry="92" fill="#5e1f22"/>')
add('<ellipse cx="600" cy="806" rx="400" ry="76" fill="#8a3a3a"/>')
add('<ellipse cx="600" cy="806" rx="360" ry="60" fill="#a86a5a" opacity="0.55"/>')
add('<ellipse cx="600" cy="806" rx="400" ry="76" fill="none" stroke="#e8c88a" stroke-width="6"/>')
add('<ellipse cx="600" cy="806" rx="430" ry="88" fill="none" stroke="#e8c88a" stroke-width="3" stroke-dasharray="14 10" opacity="0.8"/>')
# floor boards
add('<g stroke="#2e2318" stroke-width="3" opacity="0.5">')
for _x in (200, 420, 700, 950):
    add(f'<line x1="{_x}" y1="700" x2="{_x-40}" y2="900"/>')
add('</g>')
# potted ferns
for _sx, _flip in ((78, 1), (1122, -1)):
    add(f'<g transform="translate({_sx},640)">')
    add('<ellipse cx="0" cy="110" rx="52" ry="12" fill="#000" opacity="0.3" filter="url(#soft)"/>')
    add('<path d="M-42,40 L42,40 L30,110 L-30,110 Z" fill="#8a4a2a"/>')
    add('<rect x="-42" y="30" width="84" height="18" rx="6" fill="#a85e36"/>')
    for _i, (_dx, _ry, _rot) in enumerate(((-46,-30,-38), (-24,-52,-16), (0,-62,0), (24,-52,16), (46,-30,38))):
        add(f'<ellipse cx="{_dx}" cy="{_ry}" rx="14" ry="44" fill="#3f6b34" transform="rotate({_rot} {_dx} {_ry})"/>')
        add(f'<ellipse cx="{_dx}" cy="{_ry-6}" rx="6" ry="32" fill="#5d8f4e" transform="rotate({_rot} {_dx} {_ry})"/>')
    add('</g>')
# dust motes / flash dust
add('<g fill="#fff" opacity="0.25">')
add('<circle cx="320" cy="220" r="3"/><circle cx="700" cy="180" r="2.5"/>')
add('<circle cx="500" cy="300" r="2"/><circle cx="950" cy="420" r="3"/><circle cx="180" cy="500" r="2.5"/>')
add('</g>')
# ---- TEEN (left, embarrassed, leaning away) ----
add('<g transform="translate(228,470) rotate(-9)">')
# legs crossed, slouch
add('<rect x="-42" y="150" width="30" height="150" rx="12" fill="#4e446e"/>')
add('<rect x="8" y="150" width="30" height="150" rx="12" fill="#4e446e" transform="rotate(12 23 150)"/>')
add('<rect x="-58" y="290" width="52" height="20" rx="8" fill="#2e283e"/>')
add('<rect x="6" y="292" width="52" height="20" rx="8" fill="#2e283e" transform="rotate(12 32 292)"/>')
# torso lanky
add('<rect x="-58" y="-30" width="116" height="195" rx="26" fill="url(#teenBody)"/>')
add('<rect x="-58" y="-30" width="116" height="195" rx="26" fill="none" stroke="#3a3050" stroke-width="5"/>')
add('<circle cx="-38" cy="120" r="7" fill="#ff8ab5"/>')  # sticker dot
add('<path d="M18,90 l10,20 l-12,2 l8,18 l-22,-26 l12,-2 Z" fill="#ffe14d" stroke="#3a3050" stroke-width="3"/>')
add('<rect x="-46" y="-12" width="30" height="22" rx="4" fill="#3a3050" opacity="0.35"/>')  # chipped paint
# crossed arms tight
add('<rect x="-66" y="38" width="132" height="30" rx="15" fill="#8a7ab8" stroke="#3a3050" stroke-width="4"/>')
add('<rect x="-66" y="62" width="132" height="30" rx="15" fill="#9a8ac2" stroke="#3a3050" stroke-width="4"/>')
add('<circle cx="-62" cy="53" r="12" fill="#b9aad9" stroke="#3a3050" stroke-width="4"/>')
add('<circle cx="62" cy="77" r="12" fill="#b9aad9" stroke="#3a3050" stroke-width="4"/>')
# neck + head
add('<rect x="-14" y="-58" width="28" height="26" fill="#6f5f9e"/>')
add('<rect x="-48" y="-178" width="96" height="124" rx="34" fill="url(#teenBody)" stroke="#3a3050" stroke-width="5"/>')
# drooping antenna
add('<path d="M20,-178 C30,-200 10,-210 -6,-202" fill="none" stroke="#3a3050" stroke-width="5" stroke-linecap="round"/>')
add('<circle cx="-8" cy="-201" r="8" fill="#ff8ab5" stroke="#3a3050" stroke-width="3"/>')
# oversized headphones
add('<path d="M-52,-130 C-52,-190 52,-190 52,-130" fill="none" stroke="#ff6f9f" stroke-width="14" stroke-linecap="round"/>')
add('<rect x="-68" y="-142" width="28" height="52" rx="12" fill="#ff6f9f" stroke="#7a1f3f" stroke-width="4"/>')
add('<rect x="40" y="-142" width="28" height="52" rx="12" fill="#ff6f9f" stroke="#7a1f3f" stroke-width="4"/>')
# face looking hard left (away from family)
add('<ellipse cx="-22" cy="-112" rx="14" ry="16" fill="#fff"/>')
add('<ellipse cx="18" cy="-112" rx="14" ry="16" fill="#fff"/>')
add('<circle cx="-28" cy="-110" r="6" fill="#221f30"/>')  # pupils pinned left
add('<circle cx="12" cy="-110" r="6" fill="#221f30"/>')
add('<circle cx="-30" cy="-112" r="2" fill="#fff"/>')
add('<circle cx="10" cy="-112" r="2" fill="#fff"/>')
add('<rect x="-34" y="-132" width="26" height="10" rx="5" fill="#3a3050"/>')  # half-lid bored
add('<rect x="8" y="-132" width="26" height="10" rx="5" fill="#3a3050"/>')
add('<path d="M-18,-62 L14,-66" stroke="#3a3050" stroke-width="5" stroke-linecap="round"/>')  # flat mouth
add('<ellipse cx="-38" cy="-84" rx="8" ry="5" fill="#ff8ab5" opacity="0.6"/>')
add('</g>')
# ground shadows
add('<g fill="#000" opacity="0.28" filter="url(#soft)">')
add('<ellipse cx="230" cy="772" rx="110" ry="20"/>')
add('<ellipse cx="600" cy="782" rx="150" ry="22"/>')
add('<ellipse cx="835" cy="778" rx="120" ry="20"/>')
add('<ellipse cx="470" cy="848" rx="110" ry="18"/>')
add('<ellipse cx="970" cy="852" rx="100" ry="16"/>')
add('</g>')
# ---- DAD (center, stern patriarch, rigid) ----
add('<g transform="translate(600,470)">')
# legs + feet
add('<rect x="-72" y="130" width="44" height="165" rx="8" fill="#33383e" stroke="#1d2125" stroke-width="4"/>')
add('<rect x="28" y="130" width="44" height="165" rx="8" fill="#33383e" stroke="#1d2125" stroke-width="4"/>')
add('<rect x="-92" y="282" width="74" height="28" rx="10" fill="#22262b" stroke="#101215" stroke-width="3"/>')
add('<rect x="18" y="282" width="74" height="28" rx="10" fill="#22262b" stroke="#101215" stroke-width="3"/>')
# torso big box
add('<rect x="-104" y="-80" width="208" height="222" rx="14" fill="url(#dadMetal)" stroke="#23272c" stroke-width="5"/>')
# rivets
for _rx, _ry in ((-88,-64),(88,-64),(-88,126),(88,126)):
    add(f'<circle cx="{_rx}" cy="{_ry}" r="7" fill="#2c3137" stroke="#c8ced4" stroke-width="2"/>')
# chest panel gauges
add('<rect x="-78" y="-40" width="156" height="78" rx="10" fill="#2e3339" stroke="#171a1e" stroke-width="3"/>')
add('<circle cx="-38" cy="-1" r="22" fill="#e8e2d2" stroke="#171a1e" stroke-width="3"/>')
add('<line x1="-38" y1="-1" x2="-26" y2="-14" stroke="#b03030" stroke-width="4" stroke-linecap="round"/>')
add('<circle cx="38" cy="-1" r="22" fill="#e8e2d2" stroke="#171a1e" stroke-width="3"/>')
add('<line x1="38" y1="-1" x2="48" y2="-18" stroke="#2a6db0" stroke-width="4" stroke-linecap="round"/>')
add('<rect x="-52" y="52" width="104" height="12" rx="6" fill="#1d2125"/>')
add('<rect x="-52" y="70" width="104" height="12" rx="6" fill="#1d2125"/>')
add('<rect x="-52" y="88" width="70" height="12" rx="6" fill="#1d2125"/>')
# too-short crooked tie
add('<g transform="translate(0,48) rotate(7)">')
add('<rect x="-10" y="-46" width="20" height="18" fill="#7a1f22"/>')
add('<path d="M-16,-28 L16,-28 L10,34 L0,46 L-10,34 Z" fill="#a83236" stroke="#4a1315" stroke-width="3"/>')
add('</g>')
# rust patches
add('<ellipse cx="-84" cy="90" rx="16" ry="10" fill="#8a5a2a" opacity="0.7"/>')
add('<ellipse cx="80" cy="-60" rx="12" ry="8" fill="#8a5a2a" opacity="0.6"/>')
# right arm (viewer left) stiff down, hand HOVERING with gap over kid
add('<g transform="translate(-104,-60) rotate(8)">')
add('<rect x="-20" y="0" width="40" height="150" rx="14" fill="url(#dadMetal)" stroke="#23272c" stroke-width="4"/>')
add('<rect x="-26" y="148" width="52" height="44" rx="12" fill="#9aa2ac" stroke="#23272c" stroke-width="4"/>')
add('<line x1="-12" y1="170" x2="-12" y2="188" stroke="#23272c" stroke-width="3"/>')
add('<line x1="0" y1="170" x2="0" y2="188" stroke="#23272c" stroke-width="3"/>')
add('<line x1="12" y1="170" x2="12" y2="188" stroke="#23272c" stroke-width="3"/>')
add('</g>')
# left arm (viewer right) clamped on mom shoulder, stiff angle
add('<g transform="translate(104,-60) rotate(28)">')
add('<rect x="-20" y="0" width="40" height="150" rx="14" fill="url(#dadMetal)" stroke="#23272c" stroke-width="4"/>')
add('<rect x="-28" y="146" width="56" height="34" rx="12" fill="#9aa2ac" stroke="#23272c" stroke-width="4"/>')
add('</g>')
# head
add('<rect x="-82" y="-226" width="164" height="132" rx="16" fill="url(#dadHead)" stroke="#23272c" stroke-width="5"/>')
add('<rect x="-82" y="-226" width="164" height="30" rx="12" fill="#aeb6bf" opacity="0.7"/>')
# stern brow
add('<path d="M-70,-148 L-10,-138 L-10,-152 L-70,-162 Z" fill="#2c3137"/>')
add('<path d="M70,-148 L10,-138 L10,-152 L70,-162 Z" fill="#2c3137"/>')
# single visor eye slit staring at camera
add('<rect x="-62" y="-138" width="124" height="30" rx="15" fill="#141416"/>')
add('<rect x="-52" y="-130" width="104" height="14" rx="7" fill="#ffb43a"/>')
add('<circle cx="6" cy="-123" r="9" fill="#fff2c8"/>')
add('<circle cx="6" cy="-123" r="3.5" fill="#ff5a1f"/>')
add('<circle cx="-44" cy="-126" r="3" fill="#fff" opacity="0.9"/>')
# vent mouth flat disapproving
add('<rect x="-42" y="-98" width="84" height="22" rx="8" fill="#23272c"/>')
for _lx in (-30, -18, -6, 6, 18, 30):
    add(f'<line x1="{_lx}" y1="-97" x2="{_lx}" y2="-77" stroke="#7c8791" stroke-width="3"/>')
# side bolts + jaw rivets
add('<circle cx="-88" cy="-160" r="12" fill="#3a4046" stroke="#c8ced4" stroke-width="3"/>')
add('<circle cx="88" cy="-160" r="12" fill="#3a4046" stroke="#c8ced4" stroke-width="3"/>')
# top antenna + beacon
add('<rect x="-6" y="-256" width="12" height="34" fill="#33383e"/>')
add('<circle cx="0" cy="-262" r="12" fill="#c03030" stroke="#5a1010" stroke-width="3"/>')
add('<circle cx="-4" cy="-266" r="4" fill="#ffb0b0"/>')
add('<path d="M-30,-226 L30,-226" stroke="#c8ced4" stroke-width="3" opacity="0.6"/>')
add('</g>')
# ---- MOM (right-center, overeager peacemaker leaning into dad) ----
add('<g transform="translate(835,505) rotate(-9)">')
# legs + shoes
add('<rect x="-38" y="170" width="28" height="80" rx="10" fill="#4a7a65" stroke="#2e4a3e" stroke-width="4"/>')
add('<rect x="10" y="170" width="28" height="80" rx="10" fill="#4a7a65" stroke="#2e4a3e" stroke-width="4"/>')
add('<ellipse cx="-24" cy="258" rx="32" ry="14" fill="#3a2c22" stroke="#1d1510" stroke-width="3"/>')
add('<ellipse cx="24" cy="258" rx="32" ry="14" fill="#3a2c22" stroke="#1d1510" stroke-width="3"/>')
# dress body hourglass
add('<path d="M-64,-20 C-70,60 -52,120 -40,175 L40,175 C52,120 70,60 64,-20 C40,-34 -40,-34 -64,-20 Z" fill="url(#momBody)" stroke="#2e4a3e" stroke-width="5"/>')
add('<ellipse cx="0" cy="60" rx="46" ry="58" fill="#f2f7ef" stroke="#2e4a3e" stroke-width="4"/>')  # apron
add('<path d="M-14,38 c-8,-10 -22,-6 -18,6 c3,9 18,18 18,18 c0,0 15,-9 18,-18 c4,-12 -10,-16 -18,-6 Z" fill="#d94a5a" stroke="#7a1f2a" stroke-width="3"/>')
add('<circle cx="0" cy="6" r="6" fill="#d94a5a"/>')
# pearl necklace
for _px in (-24, -12, 0, 12, 24):
    add(f'<circle cx="{_px}" cy="-16" r="7" fill="#f5f0e6" stroke="#8a8072" stroke-width="2"/>')
# right arm clutching dad (extended left, tight grip)
add('<g transform="translate(-62,0) rotate(-18)">')
add('<rect x="-18" y="0" width="36" height="110" rx="16" fill="url(#momBody)" stroke="#2e4a3e" stroke-width="4"/>')
add('<circle cx="0" cy="122" r="20" fill="#c8e8d5" stroke="#2e4a3e" stroke-width="4"/>')
add('<path d="M-12,116 L12,128 M-12,124 L12,136" stroke="#2e4a3e" stroke-width="3"/>')
add('</g>')
# left arm stiff little wave
add('<g transform="translate(62,0) rotate(24)">')
add('<rect x="-16" y="0" width="32" height="100" rx="14" fill="url(#momBody)" stroke="#2e4a3e" stroke-width="4"/>')
add('<circle cx="0" cy="116" r="18" fill="#c8e8d5" stroke="#2e4a3e" stroke-width="4"/>')
add('<line x1="-8" y1="128" x2="-12" y2="144" stroke="#2e4a3e" stroke-width="3" stroke-linecap="round"/>')
add('<line x1="0" y1="130" x2="0" y2="146" stroke="#2e4a3e" stroke-width="3" stroke-linecap="round"/>')
add('<line x1="8" y1="128" x2="12" y2="144" stroke="#2e4a3e" stroke-width="3" stroke-linecap="round"/>')
add('</g>')
# neck
add('<rect x="-12" y="-52" width="24" height="26" fill="#6da88d"/>')
# glass dome head with brain coils
add('<circle cx="0" cy="-116" r="68" fill="#bfe0ea" stroke="#2e4a3e" stroke-width="5"/>')
add('<path d="M-40,-150 C-20,-170 20,-170 40,-150" fill="none" stroke="#7a9fb0" stroke-width="4"/>')
add('<circle cx="-16" cy="-142" r="12" fill="none" stroke="#5a7f95" stroke-width="4"/>')
add('<circle cx="12" cy="-146" r="14" fill="none" stroke="#5a7f95" stroke-width="4"/>')
add('<circle cx="0" cy="-116" r="68" fill="url(#glassShine)"/>')
# huge eyes gazing up-left at dad (love-struck, wrong direction)
add('<ellipse cx="-24" cy="-112" rx="17" ry="20" fill="#fff" stroke="#2e4a3e" stroke-width="3"/>')
add('<ellipse cx="24" cy="-112" rx="17" ry="20" fill="#fff" stroke="#2e4a3e" stroke-width="3"/>')
add('<circle cx="-30" cy="-116" r="8" fill="#2a4a6b"/>')
add('<circle cx="18" cy="-116" r="8" fill="#2a4a6b"/>')
add('<circle cx="-32" cy="-119" r="3" fill="#fff"/>')
add('<circle cx="16" cy="-119" r="3" fill="#fff"/>')
# eyelashes (too much mascara)
add('<path d="M-40,-128 l-10,-8 M-34,-132 l-6,-11 M40,-128 l10,-8 M34,-132 l6,-11" stroke="#2e4a3e" stroke-width="3" stroke-linecap="round"/>')
# too-wide grille smile
add('<rect x="-38" y="-78" width="76" height="30" rx="15" fill="#3a2c22" stroke="#2e4a3e" stroke-width="3"/>')
for _tx in (-26, -14, -2, 10, 22):
    add(f'<line x1="{_tx}" y1="-78" x2="{_tx}" y2="-48" stroke="#e8e2d2" stroke-width="3"/>')
# blush + beauty-mark rivet
add('<ellipse cx="-44" cy="-88" rx="10" ry="6" fill="#ff9a9a" opacity="0.8"/>')
add('<ellipse cx="44" cy="-88" rx="10" ry="6" fill="#ff9a9a" opacity="0.8"/>')
add('<circle cx="38" cy="-70" r="4" fill="#3a2c22"/>')
# curly antennae hair + bow
add('<path d="M-52,-164 C-78,-182 -78,-210 -58,-208 C-46,-206 -48,-192 -58,-192" fill="none" stroke="#2e4a3e" stroke-width="5" stroke-linecap="round"/>')
add('<path d="M52,-164 C78,-182 78,-210 58,-208 C46,-206 48,-192 58,-192" fill="none" stroke="#2e4a3e" stroke-width="5" stroke-linecap="round"/>')
add('<circle cx="-58" cy="-208" r="9" fill="#d94a5a" stroke="#7a1f2a" stroke-width="3"/>')
add('<circle cx="58" cy="-208" r="9" fill="#d94a5a" stroke="#7a1f2a" stroke-width="3"/>')
add('<path d="M40,-172 l14,-16 l4,18 l16,-2 l-14,12 l8,14 l-18,-6 l-12,12 l0,-18 Z" fill="#ff6f9f" stroke="#7a1f3f" stroke-width="2"/>')
add('</g>')
# ---- KID (front-center, feral little brother, too close) ----
add('<g transform="translate(470,650)">')
# legs tiptoe, one foot lifted
add('<rect x="-36" y="110" width="28" height="60" rx="10" fill="#7a3f0e" stroke="#3a1f05" stroke-width="4"/>')
add('<rect x="8" y="110" width="28" height="60" rx="10" fill="#7a3f0e" stroke="#3a1f05" stroke-width="4" transform="rotate(-14 22 110)"/>')
add('<ellipse cx="-22" cy="176" rx="30" ry="13" fill="#2e1a08"/>')
add('<ellipse cx="34" cy="170" rx="30" ry="13" fill="#2e1a08" transform="rotate(-14 34 170)"/>')
# body small dented
add('<rect x="-56" y="10" width="112" height="112" rx="18" fill="url(#kidBody)" stroke="#5a2e08" stroke-width="5"/>')
add('<rect x="-38" y="30" width="76" height="56" rx="10" fill="#5a2e08"/>')
add('<circle cx="-14" cy="52" r="10" fill="#ff4d4d" stroke="#3a1f05" stroke-width="2"/>')
add('<circle cx="14" cy="52" r="10" fill="#4dd2ff" stroke="#3a1f05" stroke-width="2"/>')
add('<rect x="-26" y="70" width="52" height="8" rx="4" fill="#3a1f05"/>')
add('<ellipse cx="-44" cy="20" rx="12" ry="7" fill="#7a3f0e" opacity="0.6"/>')
# left arm down holding upside-down toy rocket
add('<g transform="translate(56,40) rotate(18)">')
add('<rect x="-14" y="0" width="28" height="66" rx="12" fill="url(#kidBody)" stroke="#5a2e08" stroke-width="4"/>')
add('<g transform="translate(0,92) rotate(180)">')
add('<path d="M-16,0 L16,0 L8,-34 L0,-42 L-8,-34 Z" fill="#d94a5a" stroke="#5a1420" stroke-width="3"/>')
add('<circle cx="0" cy="-14" r="7" fill="#bfe0ea" stroke="#5a1420" stroke-width="2"/>')
add('<path d="M-16,0 L-24,12 L-14,10 Z M16,0 L24,12 L14,10 Z" fill="#5a1420"/>')
add('</g>')
add('</g>')
# right arm WAY up waving in front of mom face
add('<g transform="translate(-56,30) rotate(-28)">')
add('<rect x="-15" y="-108" width="30" height="118" rx="14" fill="url(#kidBody)" stroke="#5a2e08" stroke-width="4"/>')
add('<circle cx="0" cy="-122" r="22" fill="#ffb35c" stroke="#5a2e08" stroke-width="4"/>')
add('<path d="M-14,-138 L-18,-156 M-5,-141 L-6,-160 M5,-141 L7,-160 M14,-138 L19,-155" stroke="#5a2e08" stroke-width="5" stroke-linecap="round"/>')
add('</g>')
# head tilted, mismatched eyes
add('<g transform="translate(0,-38) rotate(-7)">')
add('<rect x="-64" y="-108" width="128" height="108" rx="20" fill="url(#kidBody)" stroke="#5a2e08" stroke-width="5"/>')
add('<ellipse cx="-48" cy="-80" rx="10" ry="7" fill="#7a3f0e" opacity="0.5"/>')
add('<ellipse cx="-30" cy="-58" rx="26" ry="28" fill="#fff" stroke="#5a2e08" stroke-width="4"/>')
add('<ellipse cx="34" cy="-58" rx="15" ry="16" fill="#fff" stroke="#5a2e08" stroke-width="4"/>')
add('<circle cx="-22" cy="-50" r="10" fill="#1d2a30"/>')
add('<circle cx="38" cy="-64" r="6" fill="#1d2a30"/>')
add('<circle cx="-25" cy="-53" r="3.5" fill="#fff"/>')
add('<circle cx="36" cy="-66" r="2" fill="#fff"/>')
# buck-tooth grin, one missing
add('<rect x="-44" y="-22" width="88" height="30" rx="10" fill="#3a1f05"/>')
add('<rect x="-38" y="-20" width="14" height="16" fill="#fff"/>')
add('<rect x="-22" y="-20" width="14" height="16" fill="#3a1f05" stroke="#fff" stroke-width="2"/>')
add('<rect x="-6" y="-20" width="14" height="16" fill="#fff"/>')
add('<rect x="10" y="-20" width="14" height="16" fill="#fff"/>')
add('<rect x="26" y="-20" width="12" height="12" fill="#fff"/>')
# propeller beanie
add('<rect x="-40" y="-122" width="80" height="18" rx="9" fill="#2a6db0" stroke="#14365a" stroke-width="3"/>')
add('<rect x="-4" y="-146" width="8" height="28" fill="#14365a"/>')
add('<ellipse cx="-20" cy="-148" rx="22" ry="7" fill="#ff4d4d" stroke="#5a1420" stroke-width="2"/>')
add('<ellipse cx="20" cy="-148" rx="22" ry="7" fill="#ffe14d" stroke="#5a5a14" stroke-width="2"/>')
add('</g>')
add('</g>')
# ---- DOG (front-right, glitchy pet, loyal to teen but staring at camera) ----
add('<g transform="translate(972,712)">')
# legs + tail
add('<rect x="-52" y="60" width="22" height="58" rx="9" fill="#5c656e" stroke="#2c3339" stroke-width="4"/>')
add('<rect x="-10" y="60" width="22" height="58" rx="9" fill="#5c656e" stroke="#2c3339" stroke-width="4"/>')
add('<rect x="28" y="60" width="22" height="58" rx="9" fill="#5c656e" stroke="#2c3339" stroke-width="4"/>')
add('<ellipse cx="-41" cy="122" rx="20" ry="9" fill="#22262b"/>')
add('<ellipse cx="1" cy="122" rx="20" ry="9" fill="#22262b"/>')
add('<ellipse cx="39" cy="122" rx="20" ry="9" fill="#22262b"/>')
# wag antenna tail + motion lines
add('<path d="M58,40 C86,30 92,2 88,-20" fill="none" stroke="#2c3339" stroke-width="7" stroke-linecap="round"/>')
add('<circle cx="88" cy="-28" r="11" fill="#ff4d4d" stroke="#5a1010" stroke-width="3"/>')
add('<path d="M100,-44 C108,-50 116,-50 122,-44 M102,-24 C110,-28 118,-26 124,-20" stroke="#2c3339" stroke-width="3" fill="none" stroke-linecap="round"/>')
# toaster body
add('<rect x="-70" y="-6" width="138" height="82" rx="20" fill="url(#dogBody)" stroke="#2c3339" stroke-width="5"/>')
add('<rect x="-58" y="8" width="50" height="10" rx="5" fill="#2c3339"/>')
add('<rect x="-58" y="24" width="34" height="10" rx="5" fill="#2c3339"/>')
add('<circle cx="48" cy="34" r="8" fill="#4dd2ff" stroke="#2c3339" stroke-width="2"/>')
add('<rect x="-62" y="-16" width="122" height="14" rx="7" fill="#3a4249"/>')
# collar + tag
add('<rect x="-62" y="56" width="110" height="14" fill="#a83236"/>')
add('<path d="M-6,70 c-5,-6 -13,-3 -11,3 c2,5 11,10 11,10 c0,0 9,-5 11,-10 c2,-6 -6,-9 -11,-3 Z" fill="#ffe14d" stroke="#5a4a00" stroke-width="2"/>')
# head tilted, one ear up one floppy
add('<g transform="translate(-6,-62) rotate(16)">')
add('<path d="M-52,-34 L-64,-84 L-28,-60 Z" fill="#7c8791" stroke="#2c3339" stroke-width="4"/>')
add('<path d="M52,-34 C66,-20 64,6 50,16 C40,6 38,-18 52,-34 Z" fill="#5c656e" stroke="#2c3339" stroke-width="4"/>')
add('<rect x="-58" y="-60" width="116" height="84" rx="22" fill="url(#dogBody)" stroke="#2c3339" stroke-width="5"/>')
add('<rect x="-44" y="-70" width="88" height="12" rx="6" fill="#3a4249"/>')
# googly mismatched eyes, one looking at camera one at teen
add('<ellipse cx="-24" cy="-20" rx="20" ry="22" fill="#fff" stroke="#2c3339" stroke-width="3"/>')
add('<ellipse cx="26" cy="-18" rx="13" ry="14" fill="#fff" stroke="#2c3339" stroke-width="3"/>')
add('<circle cx="-20" cy="-14" r="9" fill="#1d2a30"/>')
add('<circle cx="22" cy="-20" r="6" fill="#1d2a30"/>')
add('<circle cx="-23" cy="-17" r="3" fill="#fff"/>')
add('<circle cx="20" cy="-22" r="2" fill="#fff"/>')
# snout + lolling cable tongue
add('<rect x="-26" y="6" width="52" height="26" rx="12" fill="#3a4249"/>')
add('<ellipse cx="0" cy="12" rx="8" ry="6" fill="#22262b"/>')
add('<path d="M12,22 C20,44 34,50 30,68 C28,78 12,78 10,66 C8,54 16,44 6,30 Z" fill="#ff6f9f" stroke="#7a1f3f" stroke-width="3"/>')
add('<circle cx="20" cy="70" r="5" fill="#7a1f3f"/>')
add('</g>')
add('</g>')
# ---- photo finish: flash glints, vignette, border ----
add('<g>')
add('<circle cx="606" cy="347" r="7" fill="#fff" opacity="0.9"/>')
add('<circle cx="446" cy="534" r="5" fill="#fff" opacity="0.9"/>')
add('<circle cx="948" cy="636" r="4" fill="#fff" opacity="0.85"/>')
add('<rect x="0" y="0" width="1200" height="900" fill="none" stroke="#1d1510" stroke-width="26" opacity="0.9"/>')
add('<rect x="20" y="20" width="1160" height="860" fill="none" stroke="#f5e6c8" stroke-width="6" opacity="0.7"/>')
add('<rect x="0" y="0" width="1200" height="900" fill="#000" opacity="0.08"/>')
add('</g>')
add('</svg>')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(P), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
