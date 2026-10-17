// Dev tool: runs the page for a while in headless Chrome and reports any
// runtime noise, NaNs or shot transitions.
import puppeteer from 'puppeteer';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
execFileSync('esbuild', ['main.js', '--bundle', '--format=esm', '--outfile=tools/preview/bundle.js'], { cwd: root, stdio: 'inherit' });

const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
const server = http.createServer((req, res) => {
  const file = path.join(root, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
  if (!file.startsWith(root) || !fs.existsSync(file)) { res.writeHead(404).end('nope'); return; }
  res.writeHead(200, { 'content-type': types[path.extname(file)] || 'text/plain' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, r));

const browser = await puppeteer.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'] });
const page = await browser.newPage();
await page.setViewport({ width: 800, height: 500 });
const noise = [];
page.on('console', (m) => {
  if (m.type() === 'error' || m.type() === 'warning') noise.push(`[${m.type()}] ${m.text()}`);
});
page.on('pageerror', (e) => noise.push(`[pageerror] ${e.message}`));

await page.goto(`http://127.0.0.1:${server.address().port}/tools/preview/index.html`, { waitUntil: 'load' });
await page.waitForFunction('window.__pelican !== undefined', { timeout: 60000 });

// watch the animation for 25 real seconds
const watch = page.evaluate(async () => {
  const P = window.__pelican;
  const seen = [];
  const bad = [];
  const t0 = performance.now();
  let frames = 0;
  let lastShot = '';
  let cuts = 0;
  while (performance.now() - t0 < 25000) {
    await new Promise((r) => requestAnimationFrame(r));
    frames++;
    const s = P.rider.state;
    const nums = [s.position.x, s.position.y, s.position.z, cameraY()];
    for (const n of nums) if (!isFinite(n)) bad.push('NaN in state');
    if (lastShot && lastShot !== P.rig.shot) cuts++;
    lastShot = P.rig.shot;
    function cameraY() {
      return P.scene.children.find((c) => c.isCamera)?.position.y ?? 0;
    }
  }
  return { frames, cuts, shots: [...new Set(seen)], bad, t: P.t, lastShot };
});

const res = await watch;
console.log('frames rendered:', res.frames, ' fps ~', (res.frames / 25).toFixed(1));
console.log('shot cuts seen:', res.cuts, ' last shot:', res.lastShot);
console.log('animation time reached:', res.t.toFixed(2), 's');
console.log('bad values:', res.bad.length ? res.bad.join(', ') : 'none');
console.log('console noise:', noise.length ? '\n' + noise.join('\n') : 'none');
await browser.close();
server.close();
