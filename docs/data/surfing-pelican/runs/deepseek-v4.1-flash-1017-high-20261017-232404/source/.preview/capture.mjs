import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
  args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--hide-scrollbars'],
});
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await page.goto('http://localhost:8898/index.html', { waitUntil: 'networkidle0', timeout: 60000 });
const times = [3, 8, 20, 40];
let prev = 0;
for (const t of times) {
  await new Promise((r) => setTimeout(r, (t - prev) * 1000));
  prev = t;
  await page.screenshot({ path: `/tmp/pelican-t${t}.png` });
}
// Mobile-ish frame
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await new Promise((r) => setTimeout(r, 2500));
await page.screenshot({ path: '/tmp/pelican-mobile.png' });
console.log('errors:', JSON.stringify(errors));
await browser.close();
