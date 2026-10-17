import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--hide-scrollbars']
});
const page = await browser.newPage();
page.on('console', m => console.log('CONSOLE', m.type(), m.text()));
page.on('pageerror', e => console.log('PAGEERROR', e.message));
page.on('requestfailed', r => console.log('REQFAIL', r.url()));
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
await page.goto('http://localhost:8765/.preview/index.html', { waitUntil: 'load' });
await new Promise(r => setTimeout(r, 5000));
console.log(await page.evaluate(() => ({children: document.body.children.length, canvas: document.querySelectorAll('canvas').length, webgl: !!document.createElement('canvas').getContext('webgl2')})));
await page.screenshot({ path: '.preview/shot2.png' });
await browser.close();
