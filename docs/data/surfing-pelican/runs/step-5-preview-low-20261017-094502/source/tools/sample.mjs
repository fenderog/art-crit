// Dev tool: samples the rendered frame as a grid of hex pixels.
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
await page.setViewport({ width: 960, height: 600 });
page.on('pageerror', (e) => console.log('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/tools/preview/index.html`, { waitUntil: 'load' });
await page.waitForFunction('window.__pelican !== undefined', { timeout: 60000 });
await new Promise((r) => setTimeout(r, 3000));

const sec = Number(process.argv[2] || 0);
const grid = await page.evaluate((sec) => {
  const P = window.__pelican;
  P.seek(sec);
  const c = document.getElementById('scene');
  const o = document.createElement('canvas');
  o.width = c.width; o.height = c.height;
  const ctx = o.getContext('2d');
  ctx.drawImage(c, 0, 0);
  const rows = [];
  for (let gy = 1; gy <= 5; gy++) {
    const row = [];
    for (let gx = 1; gx <= 8; gx++) {
      const x = Math.floor((gx / 9) * o.width);
      const y = Math.floor((gy / 6) * o.height);
      const d = ctx.getImageData(x, y, 1, 1).data;
      row.push('#' + [d[0], d[1], d[2]].map((v) => v.toString(16).padStart(2, '0')).join(''));
    }
    rows.push(row.join(' '));
  }
  return { rows, shot: P.rig.shot, size: [o.width, o.height] };
}, sec);

console.log(`t=${sec} shot=${grid.shot} size=${grid.size}`);
grid.rows.forEach((r, i) => console.log(`row${i + 1}: ${r}`));
await page.screenshot({ path: path.join(root, 'tools', 'shots', `sample${sec}.png`) });
await browser.close();
server.close();
