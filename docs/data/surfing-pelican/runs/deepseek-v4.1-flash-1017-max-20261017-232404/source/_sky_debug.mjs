import puppeteer from 'puppeteer-core';
const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: ['--no-sandbox','--disable-dev-shm-usage','--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-angle=metal','--window-size=1600,900']
});
const page = await browser.newPage();
await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:4173/_test.html', { waitUntil: 'networkidle0' });
await new Promise(r=>setTimeout(r,2000));
await page.evaluate(() => {
  const w=window.__world;
  w.bloomPass.enabled=false;
  w.renderer.toneMappingExposure=1;
  w.ocean.mesh.visible=false;
  w.boardGroup.visible=false;
  w.scene.traverse(o => { if(o.isPoints) o.visible=false; });
  // hide HUD
  document.querySelector('.hud').style.display='none';
  document.querySelector('.footer-mark').style.display='none';
});
await new Promise(r=>setTimeout(r,400));
await page.screenshot({ path: 'shot_sky.png' });
await browser.close();
