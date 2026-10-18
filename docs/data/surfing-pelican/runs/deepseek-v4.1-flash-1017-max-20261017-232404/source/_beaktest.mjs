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
await new Promise(r=>setTimeout(r,2500));
await page.evaluate(() => {
  window.__world.bloomPass.enabled=false;
  window.__world.renderer.toneMappingExposure=0.8;
  window.__world.pelican.head.traverse(o => {
    if (o.isMesh && o.material.type === 'MeshPhysicalMaterial' && o.material.color && /ffa12c|ffb449/.test(o.material.color.getHexString())) {
      o.material.side=2; o.material.needsUpdate=true;
    }
  });
  // Hide the wings to make sure beak isn't occluded.
  window.__world.pelican.leftWing.wing.visible=false;
  window.__world.pelican.rightWing.wing.visible=false;
});
await new Promise(r=>setTimeout(r,500));
await page.screenshot({ path: 'shot_beak_test.png' });
await browser.close();
