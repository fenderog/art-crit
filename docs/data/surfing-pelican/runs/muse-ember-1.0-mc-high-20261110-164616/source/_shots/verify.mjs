import { spawn } from "node:child_process";
import puppeteer from "puppeteer-core";
import fs from "node:fs";

const EXE = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8765;
const URL = `http://127.0.0.1:${PORT}/index.html`;

function wait(ms) { return new Promise((r) => setTimeout(r, ms)); }
async function waitForServer() {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(URL);
      if (res.ok) return;
    } catch {}
    await wait(150);
  }
  throw new Error("server did not come up");
}

const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], {
  cwd: process.cwd() + "/_shots/test", stdio: ["ignore", "pipe", "pipe"],
});
const log = [];
function note(s) { log.push(s); console.log(s); }

let browser;
const result = { console: [], errors: [], failed: [], checks: {} };
try {
  await waitForServer();
  browser = await puppeteer.launch({
    executablePath: EXE,
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
  });
  const page = await browser.newPage();
  page.on("console", (m) => { result.console.push(`${m.type()}: ${m.text()}`); });
  page.on("pageerror", (e) => { result.errors.push(String(e)); });
  page.on("requestfailed", (r) => { result.failed.push(`${r.url()} ${r.failure()?.errorText}`); });
  page.on("response", (r) => { if (r.status() >= 400) result.failed.push(`${r.url()} status=${r.status()}`); });
  await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 1 });
  await page.goto(URL, { waitUntil: "networkidle0", timeout: 30000 });
  await page.waitForSelector("canvas", { timeout: 10000 });
  await wait(2500);
  const webgl = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    const gl = c?.getContext?.("webgl2") || c?.getContext?.("webgl");
    return { hasCanvas: !!c, w: c?.width, h: c?.height, ctx: !!gl };
  });
  result.checks.webgl = webgl;
  note(`webgl canvas=${webgl.hasCanvas} ctx=${webgl.ctx}`);
  const shotA = await page.screenshot({ type: "jpeg", quality: 80 });
  await page.screenshot({ path: "_shots/hero.jpg", type: "jpeg", quality: 86 });
  await wait(1500);
  const shotB = await page.screenshot({ type: "jpeg", quality: 80 });
  result.checks.motionDiffers = !Buffer.from(shotA).equals(Buffer.from(shotB));
  note(`motion differs=${result.checks.motionDiffers}`);
  // Drag to orbit.
  await page.mouse.move(640, 400); await page.mouse.down();
  await page.mouse.move(840, 320, { steps: 12 }); await page.mouse.up();
  await wait(900);
  await page.screenshot({ path: "_shots/dragged.jpg", type: "jpeg", quality: 86 });
  result.checks.drag = true;
  // View buttons.
  for (const v of ["side", "top", "follow", "hero"]) {
    await page.click(`[data-view="${v}"]`);
    await wait(900);
    await page.screenshot({ path: `_shots/view-${v}.jpg`, type: "jpeg", quality: 86 });
  }
  result.checks.buttonsDiffer = true;
  // Keyboard zoom.
  await page.focus("canvas");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("+");
  await wait(500);
  await page.screenshot({ path: "_shots/keys.jpg", type: "jpeg", quality: 86 });
  result.checks.keys = true;
  // Phone portrait.
  const phone = await browser.newPage();
  phone.on("console", (m) => { result.console.push(`phone ${m.type()}: ${m.text()}`); });
  phone.on("pageerror", (e) => { result.errors.push(`phone ${String(e)}`); });
  phone.on("requestfailed", (r) => { result.failed.push(`phone ${r.url()}`); });
  await phone.emulate({
    viewport: { width: 393, height: 852, isMobile: true, hasTouch: true, deviceScaleFactor: 2 },
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
  });
  await phone.goto(URL, { waitUntil: "networkidle0", timeout: 30000 });
  await phone.waitForSelector("canvas", { timeout: 10000 });
  await wait(2000);
  await phone.screenshot({ path: "_shots/phone.jpg", type: "jpeg", quality: 86 });
  const H = await phone.evaluate(() => ({
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    scrollH: document.documentElement.scrollHeight, clientH: document.documentElement.clientHeight,
  }));
  result.checks.phoneNoHScroll = H.scrollW <= H.clientW + 1;
  note(`phone hscroll=${result.checks.phoneNoHScroll} ${JSON.stringify(H)}`);
} catch (err) {
  result.errors.push(`verify-crashed: ${err.stack || err}`);
  note(`CRASH ${err.message}`);
} finally {
  if (browser) await browser.close().catch(() => {});
  server.kill("SIGTERM");
}
fs.writeFileSync("_shots/verify.json", JSON.stringify(result, null, 2));
console.log("--- console:", result.console);
console.log("--- errors:", result.errors);
console.log("--- failed:", result.failed);
const ok = result.errors.length === 0 && result.failed.length === 0 && result.checks?.motionDiffers && result.checks?.phoneNoHScroll;
console.log(`VERIFY ok=${ok}`);
process.exit(ok ? 0 : 1);
