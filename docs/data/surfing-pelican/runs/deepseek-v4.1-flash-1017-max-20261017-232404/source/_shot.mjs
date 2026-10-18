import puppeteer from 'puppeteer-core';

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--ignore-gpu-blocklist',
    '--enable-unsafe-swiftshader',
    '--use-angle=metal',
    '--window-size=1600,900'
  ]
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
const logs = [];
page.on('console', (msg) => logs.push(`[console:${msg.type()}] ${msg.text()}`));
page.on('pageerror', (err) => logs.push(`[pageerror] ${err.stack || err.message}`));
await page.goto('http://127.0.0.1:4173/_test.html', { waitUntil: 'networkidle0' });
await new Promise((r) => setTimeout(r, 5000));
await page.screenshot({ path: 'shot.png' });
const info = await page.evaluate(() => {
  const c = document.querySelector('#scene');
  const gl = c.getContext('webgl2') || c.getContext('webgl');
  return {
    bodyClass: document.body.className,
    canvas: [c.width, c.height],
    webgl: !!gl,
    renderer: gl ? gl.getParameter(gl.RENDERER) : null,
    ready: document.readyState
  };
});
console.log(JSON.stringify(info, null, 2));
console.log(logs.join('\n'));
await browser.close();
