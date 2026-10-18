import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox','--disable-dev-shm-usage','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=metal','--window-size=1600,900']
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:4173/_test.html', { waitUntil: 'networkidle0' });
await new Promise(r=>setTimeout(r,3000));
await page.evaluate(() => { window.__world.wake.mesh.visible=false; });
await new Promise(r=>setTimeout(r,400));
await page.screenshot({ path: 'shot_nowake.png' });
await page.evaluate(() => {
  window.__world.spray.points.visible=false;
  window.__world.wake.mesh.visible=true;
});
await new Promise(r=>setTimeout(r,400));
await page.screenshot({ path: 'shot_nospray_wake.png' });
await browser.close();
