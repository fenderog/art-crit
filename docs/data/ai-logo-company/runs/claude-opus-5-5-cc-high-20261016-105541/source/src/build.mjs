// Generates the "loam" logo suite as hand-tuned, dependency-free SVG.
// Usage: node src/build.mjs   (writes SVGs to ./output)
import { writeFileSync, mkdirSync } from "node:fs";

const OUT = new URL("../output/", import.meta.url);
mkdirSync(OUT, { recursive: true });

// Neutral, earth-derived palette
const C = {
  bone: "#F3EEE6",
  oat: "#E4D9C8",
  sand: "#CDBA9F",
  clay: "#AE8E71",
  umber: "#7C624D",
  bark: "#4A3D33",
  char: "#2B2622",
  stone: "#8F877D",
};

const f = (n) => +n.toFixed(2);

// Closed Catmull-Rom spline -> cubic Bézier path
function smoothClosed(pts) {
  const n = pts.length;
  const P = (i) => pts[(i + n) % n];
  let d = `M${f(pts[0][0])} ${f(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += `C${f(c1[0])} ${f(c1[1])} ${f(c2[0])} ${f(c2[1])} ${f(p2[0])} ${f(p2[1])}`;
  }
  return d + "Z";
}

// An organic pebble outline: low-frequency harmonics on a circle
function pebble({ cx, cy, r, twist = 0, amp = 1, n = 14 }) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const t = (i / n) * Math.PI * 2;
    const k =
      1 +
      amp *
        (0.075 * Math.cos(2 * (t - 0.62 - twist)) +
          0.035 * Math.sin(3 * t + 1.1 + twist * 1.6) +
          0.012 * Math.cos(5 * t + 0.4 - twist));
    pts.push([cx + Math.cos(t) * r * k, cy + Math.sin(t) * r * k]);
  }
  return smoothClosed(pts);
}

// The mark: nested strata, like a river stone cut open or growth rings
// drifting toward a dark seed — the growth front. Drawn in a 240×240 box.
function markLayers(palette) {
  const rings = [
    { r: 108, fill: palette[0] },
    { r: 86, fill: palette[1] },
    { r: 65, fill: palette[2] },
    { r: 45, fill: palette[3] },
    { r: 26, fill: palette[4] },
  ];
  const drift = [24, -20]; // strata drift toward upper-right: the growth front
  const out = rings.map((ring, k) => {
    const t = Math.pow(k / (rings.length - 1), 1.15);
    return `<path fill="${ring.fill}" d="${pebble({
      cx: 120 + drift[0] * t,
      cy: 122 + drift[1] * t,
      r: ring.r,
      twist: k * 0.2,
      amp: k === rings.length - 1 ? 1.05 : 1 - k * 0.1,
    })}"/>`;
  });
  return out.join("");
}

const LIGHT = [C.oat, C.sand, C.clay, C.umber, C.char];
const DARK = [C.bark, C.umber, C.clay, C.sand, C.bone];

// Custom monoline wordmark "loam" (round caps, soft terminals).
// Units: baseline y=0, x-height 1. Returns path data in given scale/origin.
function wordmark(x0, base, xh, sw) {
  const s = (v) => f(v * xh);
  const X = (v) => f(x0 + v * xh);
  const Y = (v) => f(base - v * xh);
  const r = 0.5 - sw / xh / 2; // bowl radius in units, centred on stroke
  const parts = [];
  let x = 0;

  // l — tall stem with a soft rolled foot
  const lx = x + sw / xh / 2;
  parts.push(
    `M${X(lx)} ${Y(1.52)}V${Y(0.22)}Q${X(lx)} ${Y(0)} ${X(lx + 0.2)} ${Y(0)}`
  );
  x = lx + 0.2 + 0.11;

  // o and a share one softly irregular bowl that echoes the pebble
  const bk = (t) => 1 + 0.022 * Math.cos(2 * (t - 0.62)) + 0.01 * Math.sin(3 * t + 1.1);
  const bowl = (cx) => {
    const pts = [];
    for (let i = 0; i < 12; i++) {
      const t = (i / 12) * Math.PI * 2;
      pts.push([x0 + (cx + Math.cos(t) * r * bk(t) * 1.02) * xh, base - (0.5 + Math.sin(t) * r * bk(t)) * xh]);
    }
    return smoothClosed(pts);
  };
  // rightmost extent of the bowl, so the a's stem sits tangent to it
  let bowlR = 0;
  for (let i = 0; i < 360; i++) {
    const t = (i / 360) * Math.PI * 2;
    bowlR = Math.max(bowlR, Math.cos(t) * r * bk(t) * 1.02);
  }

  // o
  const ocx = x + r + sw / xh / 2;
  parts.push(bowl(ocx));
  x = ocx + r + sw / xh / 2 + 0.19;

  // a — single-storey: bowl + stem
  const acx = x + r + sw / xh / 2;
  parts.push(bowl(acx));
  parts.push(`M${X(acx + bowlR)} ${Y(1 - sw / xh / 2)}V${Y(sw / xh / 2)}`);
  x = acx + bowlR + sw / xh / 2 + 0.2;

  // m — one continuous stroke: stem rolling into two arches, no spurs
  const mr = 0.27;
  const m0 = x + sw / xh / 2;
  const top = 1 - sw / xh / 2;
  const bot = sw / xh / 2;
  const sh = top - mr; // shoulder height
  parts.push(
    `M${X(m0)} ${Y(bot)}V${Y(sh)}A${s(mr)} ${s(mr)} 0 0 1 ${X(m0 + 2 * mr)} ${Y(sh)}V${Y(bot)}` +
      `M${X(m0 + 2 * mr)} ${Y(sh)}A${s(mr)} ${s(mr)} 0 0 1 ${X(m0 + 4 * mr)} ${Y(sh)}V${Y(bot)}`
  );
  x = m0 + 4 * mr + sw / xh / 2;

  return { d: parts.join(""), width: x * xh };
}

function svg(w, h, body, title, display = 1) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w * display}" height="${h * display}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${title}"><title>${title}</title>${body}</svg>\n`;
}

const LOCKUP_W = 760, LOCKUP_H = 300;
function lockupBody({ palette, ink }) {
  const mx = 50, my = 30; // mark is 240px
  const xh = 92, sw = 15;
  const base = my + 120 + xh * 0.5;
  const wm = wordmark(mx + 240 + 46, base, xh, sw);
  return (
    `<g transform="translate(${mx} ${my})">${markLayers(palette)}</g>` +
    `<path d="${wm.d}" fill="none" stroke="${ink}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"/>`
  );
}
const lockup = ({ bg, palette, ink }) =>
  svg(LOCKUP_W, LOCKUP_H, `<rect width="${LOCKUP_W}" height="${LOCKUP_H}" fill="${bg}"/>` + lockupBody({ palette, ink }), "loam — generative intelligence");

// App icon: the mark on an oat squircle
function iconBody() {
  return (
    `<rect width="512" height="512" rx="116" fill="${C.bone}"/>` +
    `<g transform="translate(256 258) scale(1.5) translate(-122 -112)">${markLayers(LIGHT)}</g>`
  );
}

writeFileSync(new URL("loam-logo-light.svg", OUT), lockup({ bg: C.bone, palette: LIGHT, ink: C.char }));
writeFileSync(new URL("loam-logo-dark.svg", OUT), lockup({ bg: C.char, palette: DARK, ink: C.bone }));
writeFileSync(new URL("loam-mark.svg", OUT), svg(240, 240, markLayers(LIGHT), "loam mark"));
writeFileSync(new URL("loam-app-icon.svg", OUT), svg(512, 512, iconBody(), "loam app icon"));

// Brand sheet (rendered to PNG by src/render.sh; the SVG itself stays in ./tmp)
{
  const W = 1600, H = 1000;
  const font = `font-family="Helvetica Neue, Helvetica, Arial, sans-serif"`;
  let b = `<rect width="${W}" height="${H}" fill="#E9E2D7"/>`;
  const card = (x, y, w, h, fill) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="28" fill="${fill}"/>`;
  b += card(40, 40, 980, 400, C.bone);
  b += `<g transform="translate(${40 + (980 - LOCKUP_W * 1.2) / 2} ${40 + (400 - LOCKUP_H * 1.2) / 2}) scale(1.2)">${lockupBody({ palette: LIGHT, ink: C.char })}</g>`;
  b += card(40, 480, 980, 400, C.char);
  b += `<g transform="translate(${40 + (980 - LOCKUP_W * 1.2) / 2} ${480 + (400 - LOCKUP_H * 1.2) / 2}) scale(1.2)">${lockupBody({ palette: DARK, ink: C.bone })}</g>`;
  // icon
  b += card(1060, 40, 500, 400, C.oat);
  b += `<g transform="translate(${1060 + 250 - 140} ${240 - 140}) scale(${280 / 512})">${iconBody()}</g>`;
  // palette + small sizes
  b += card(1060, 480, 500, 400, C.bone);
  const sw = [["bone", C.bone], ["oat", C.oat], ["sand", C.sand], ["clay", C.clay], ["umber", C.umber], ["bark", C.bark], ["char", C.char]];
  sw.forEach(([name, hex], i) => {
    const cx = 1060 + 58 + i * 64, cy = 560;
    b += `<path d="${pebble({ cx, cy, r: 25, twist: i * 0.7, amp: 1.3 })}" fill="${hex}" stroke="${i === 0 ? C.oat : "none"}" stroke-width="2"/>`;
    b += `<text x="${cx}" y="${cy + 48}" ${font} font-size="13" fill="${C.bark}" text-anchor="middle">${name}</text>`;
    b += `<text x="${cx}" y="${cy + 66}" ${font} font-size="10.5" fill="${C.stone}" text-anchor="middle" letter-spacing="0.3">${hex.slice(1)}</text>`;
  });
  b += `<line x1="1100" y1="668" x2="1520" y2="668" stroke="${C.oat}" stroke-width="2"/>`;
  [96, 64, 40, 24, 16].reduce((x, size) => {
    b += `<g transform="translate(${x} ${790 - size / 2}) scale(${size / 240})">${markLayers(LIGHT)}</g>`;
    b += `<text x="${x + size / 2}" y="852" ${font} font-size="12" fill="${C.stone}" text-anchor="middle">${size}px</text>`;
    return x + size + 44;
  }, 1112);
  b += `<text x="40" y="944" ${font} font-size="20" fill="${C.bark}" letter-spacing="0.4"><tspan font-weight="600">loam</tspan>  ·  generative intelligence, grown from the ground up</text>`;
  b += `<text x="1560" y="944" ${font} font-size="15" fill="${C.stone}" text-anchor="end">Mark: five nested strata drifting toward a single seed</text>`;
  mkdirSync(new URL("../tmp/", import.meta.url), { recursive: true });
  writeFileSync(new URL("../tmp/loam-brand-sheet.svg", import.meta.url), svg(W, H, b, "loam brand sheet", 0.4));
}
console.log("built");
