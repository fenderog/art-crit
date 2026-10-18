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
const data = await page.evaluate(async () => {
  const THREE = await import('data:text/javascript,export default {}'); // no
  const w = window.__world;
  const head = w.pelican.head;
  head.updateWorldMatrix(true, true);
  const out = [];
  head.traverse(o => {
    if (o.isMesh) {
      o.geometry.computeBoundingBox();
      const bb = o.geometry.boundingBox;
      const center = bb.getCenter(new (o.position.constructor)());
      o.localToWorld(center);
      const proj = center.clone().project(w.camera);
      out.push({
        type: o.geometry.type,
        mat: o.material.type,
        color: o.material.color ? o.material.color.getHexString() : null,
        side: o.material.side,
        bb: [bb.min.toArray().map(n=>+n.toFixed(2)), bb.max.toArray().map(n=>+n.toFixed(2))],
        world: center.toArray().map(n=>+n.toFixed(2)),
        screen: [Math.round((proj.x*.5+.5)*1600), Math.round((-proj.y*.5+.5)*900)],
        visible: o.visible
      });
    }
  });
  return out;
});
console.log(JSON.stringify(data, null, 2));
await browser.close();
