// Dev tool: bundles main.js the way the final packaging will, renders it in
// headless Chrome (software WebGL) and writes screenshots so the scene can be
// checked without a display.
//   node tools/shoot.mjs [seconds ...]

import puppeteer from 'puppeteer';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
const outDir = path.join(root, 'tools', 'shots');
const prevDir = path.join(root, 'tools', 'preview');
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(prevDir, { recursive: true });

// --- bundle exactly like the shipped page will be bundled -------------------
execFileSync(
  'esbuild',
  ['main.js', '--bundle', '--format=esm', '--outfile=tools/preview/bundle.js'],
  { cwd: root, stdio: 'inherit' },
);

const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
const server = http.createServer((req, res) => {
  const file = path.join(root, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
  if (!file.startsWith(root) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    res.writeHead(404).end('nope');
    return;
  }
  res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, r));
const port = server.address().port;

const times = process.argv.slice(2).map(Number);
const shots = times.length ? times : [0, 6, 15, 22, 31, 39, 44, 50];

const browser = await puppeteer.launch({
  args: [
    '--no-sandbox',
    '--enable-unsafe-swiftshader',
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--disable-dev-shm-usage',
  ],
});

const page = await browser.newPage();
await page.setViewport({ width: 960, height: 600, deviceScaleFactor: 1 });

const errors = [];
page.on('console', (m) => {
  if (m.type() === 'error' || m.type() === 'warning') errors.push(`[${m.type()}] ${m.text()}`);
});
page.on('pageerror', (e) => errors.push(`[pageerror] ${e.message}`));
page.on('requestfailed', (r) => errors.push(`[reqfail] ${r.url()} ${r.failure()?.errorText}`));

await page.goto(`http://127.0.0.1:${port}/tools/preview/index.html`, { waitUntil: 'load' });
await page.waitForFunction('window.__pelican !== undefined', { timeout: 60000 });

// let it run for a few real frames first (warms up shaders, spawns spray)
await new Promise((r) => setTimeout(r, 3000));

for (const s of shots) {
  await page.evaluate((sec) => window.__pelican.seek(sec), s);
  await new Promise((r) => setTimeout(r, 400));
  const name = `t${String(Math.round(s)).padStart(3, '0')}.png`;
  await page.screenshot({ path: path.join(outDir, name) });
  const info = await page.evaluate(() => ({
    shot: window.__pelican.rig.shot,
    y: window.__pelican.rider.state.position.y.toFixed(2),
  }));
  console.log(`wrote ${name}  shot=${info.shot}  riderY=${info.y}`);
}

console.log(errors.length ? `\nconsole noise:\n${errors.join('\n')}` : '\nno console errors');
await browser.close();
server.close();
