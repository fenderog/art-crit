import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox','--disable-dev-shm-usage','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=metal','--window-size=1600,900']
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
page.on('pageerror', e => console.log('ERR', e.stack||e.message));
await page.goto('http://127.0.0.1:4173/_test.html', { waitUntil: 'networkidle0' });
await new Promise(r=>setTimeout(r,3000));
await page.screenshot({ path: 'shot_bloom.png' });
await page.evaluate(() => { window.__world.bloomPass.enabled=false; });
await new Promise(r=>setTimeout(r,300));
await page.screenshot({ path: 'shot_flat.png' });
await browser.close();
