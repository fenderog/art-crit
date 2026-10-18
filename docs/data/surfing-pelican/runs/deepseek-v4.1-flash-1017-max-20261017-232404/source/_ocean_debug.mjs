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
await new Promise(r=>setTimeout(r,2200));
await page.evaluate(() => {
  window.__world.bloomPass.enabled=false;
  window.__world.renderer.toneMappingExposure=1;
  const m = window.__world.ocean.material;
  m.fragmentShader = `
    varying float vHeight;
    varying vec3 vNormalW;
    varying vec3 vWorldPos;
    void main() {
      vec3 N = normalize(vNormalW);
      float diff = max(dot(N, normalize(vec3(-0.4, 0.7, 0.6))), 0.0);
      float h = clamp(vHeight * 0.32 + 0.2, 0.0, 1.0);
      vec3 col = mix(vec3(0.015,0.08,0.13), vec3(0.08,0.38,0.46), h);
      col += vec3(0.25,0.35,0.35) * diff;
      float dist = length(cameraPosition.xz - vWorldPos.xz);
      col = mix(col, vec3(0.95,0.55,0.45), smoothstep(55.0,112.0,dist));
      gl_FragColor = vec4(col,1.0);
    }
  `;
  m.needsUpdate = true;
  window.__world.sky.group.visible = false;
  // hide the distant islands? leave, maybe
});
await new Promise(r=>setTimeout(r,600));
await page.screenshot({ path: 'shot_ocean_debug.png' });
await browser.close();
