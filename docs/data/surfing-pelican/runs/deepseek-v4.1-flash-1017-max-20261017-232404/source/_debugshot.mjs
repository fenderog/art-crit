import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox','--disable-dev-shm-usage','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=metal','--window-size=1600,900']
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
const errors=[];
page.on('pageerror', e => errors.push(e.stack||e.message));
page.on('console', m => { if (m.type()==='error') errors.push(m.text()); });
await page.goto('http://127.0.0.1:4173/_test.html', { waitUntil: 'networkidle0' });
await new Promise(r=>setTimeout(r,3000));
// Stop at a deterministic-looking moment by just screenshotting now.
await page.evaluate(() => {
  window.__world.bloomPass.enabled = false;
  window.__world.renderer.toneMappingExposure = 0.8;
});
await new Promise(r=>setTimeout(r,600));
await page.screenshot({ path: 'shot_nobloom.png' });
await page.evaluate(() => {
  window.__world.bloomPass.enabled = true;
  window.__world.bloomPass.strength = 0.25;
  window.__world.renderer.toneMappingExposure = 0.75;
});
await new Promise(r=>setTimeout(r,600));
await page.screenshot({ path: 'shot_lowbloom.png' });
console.log(errors.join('\n'));
await browser.close();
