import { createServer } from "http";
import { readFile, writeFile } from "fs/promises";
import { existsSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import puppeteer from "puppeteer-core";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const port = 5173;

// bundle first (so bare specifier "three" works in the browser without import maps)
console.log("bundling with esbuild...");
execSync("npx esbuild main.js --bundle --format=esm --outfile=bundle.js --log-level=warning", { cwd: __dirname, stdio: "inherit" });
console.log("bundle ok", existsSync(path.join(__dirname, "bundle.js")));

// also create a view html that points at the bundle (original index.html kept as-is for delivery)
const orig = await readFile(path.join(__dirname, "index.html"), "utf8");
const viewHtml = orig.replace('src="main.js"', 'src="bundle.js"');
await writeFile(path.join(__dirname, "view.html"), viewHtml);

const mime = { ".html":"text/html", ".js":"text/javascript", ".mjs":"text/javascript", ".json":"application/json", ".css":"text/css", ".jpg":"image/jpeg", ".png":"image/png" };
const server = createServer(async (req, res) => {
  let urlPath = req.url.split("?")[0];
  if (urlPath === "/") urlPath = "/view.html";
  const filePath = path.join(__dirname, urlPath);
  if (!existsSync(filePath)) { res.writeHead(404); res.end("not found"); return; }
  // view.html is the preview; index.html still loads main.js but would 404 on bare specifier without bundle
  // so serve view.html for "/" and for /index.html serve the bundled version too (for screenshot only)
  let data = await readFile(filePath);
  if (urlPath === "/index.html") {
    // serve bundled variant so the "index.html" screenshot works
    data = Buffer.from(viewHtml);
  }
  const ext = path.extname(filePath).toLowerCase();
  res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream", "Cache-Control": "no-store" });
  res.end(data);
});
await new Promise(r => server.listen(port, "127.0.0.1", r));
console.log(`serving http://127.0.0.1:${port}/`);

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu-sandbox", "--enable-unsafe-swiftshader", "--use-gl=swiftshader", "--disable-dev-shm-usage", "--window-size=1280,800"]
});

const page = await browser.newPage();
page.on("console", m => {
  const t = m.type();
  if (t === "error" || t === "warn") console.log(`[console.${t}]`, m.text());
});
page.on("pageerror", e => console.log("[pageerror]", e.message));
await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 1 });
await page.goto(`http://127.0.0.1:${port}/view.html`, { waitUntil: "networkidle0", timeout: 20000 });
await new Promise(r => setTimeout(r, 4500));
const info = await page.evaluate(() => {
  const c = document.querySelector("canvas");
  return { hasCanvas: !!c, w: c?.width, h: c?.height, ctype: c ? c.constructor.name : null };
});
console.log("canvas info", info);

await page.screenshot({ path: path.join(__dirname, "shot-desktop.jpg"), type: "jpeg", quality: 82 });
await new Promise(r => setTimeout(r, 1200));
await page.screenshot({ path: path.join(__dirname, "shot-desktop-2.jpg"), type: "jpeg", quality: 82 });

await browser.close();
server.close();
console.log("done");
