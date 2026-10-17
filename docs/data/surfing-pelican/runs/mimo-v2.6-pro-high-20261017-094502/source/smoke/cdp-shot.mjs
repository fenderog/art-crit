// Dev-only helper: screenshots a running page via the Chrome DevTools protocol.
// Usage: node smoke/cdp-shot.mjs <url-substring> <out-prefix> <delayMs> [<delayMs> ...]
// Reloads the page first, then captures a screenshot at each delay (relative to
// the reload). Console messages are collected between the first and last shot.
import { writeFileSync } from "node:fs";

const [, , targetUrl, outPrefix, ...delays] = process.argv;
if (!targetUrl || !outPrefix || delays.length === 0) {
  console.error("usage: node smoke/cdp-shot.mjs <url> <prefix> <delayMs...>");
  process.exit(1);
}
const times = delays.map(Number).sort((a, b) => a - b);

const list = await fetch("http://127.0.0.1:9333/json/list").then((r) => r.json());
const page = list.find((t) => t.type === "page" && t.url.includes(targetUrl));
if (!page) {
  console.error("no page target for", targetUrl, list.map((t) => t.url));
  process.exit(1);
}

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const logs = [];

function send(method, params = {}) {
  const msgId = ++id;
  ws.send(JSON.stringify({ id: msgId, method, params }));
  return new Promise((res) => pending.set(msgId, res));
}

ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    pending.get(msg.id)(msg.result);
    pending.delete(msg.id);
  } else if (msg.method === "Runtime.consoleAPICalled") {
    logs.push(`[${msg.params.type}] ${msg.params.args.map((a) => a.value ?? a.description).join(" ")}`);
  } else if (msg.method === "Runtime.exceptionThrown") {
    logs.push(`[exception] ${msg.params.exceptionDetails.text} ${msg.params.exceptionDetails.exception?.description ?? ""}`);
  }
};

await new Promise((res) => (ws.onopen = res));
await send("Runtime.enable");
await send("Page.enable");
await send("Page.reload", { ignoreCache: true });

let last = 0;
for (const at of times) {
  await new Promise((res) => setTimeout(res, at - last));
  last = at;
  const shot = await send("Page.captureScreenshot", { format: "png", fromSurface: true });
  const file = `${outPrefix}-${at}.png`;
  writeFileSync(file, Buffer.from(shot.data, "base64"));
  console.log("saved", file);
}

const perf = await send("Runtime.evaluate", {
  expression: `JSON.stringify({ title: document.title, canvas: !!document.querySelector('canvas') })`,
  returnByValue: true,
});
console.log("page:", perf.result.value);
console.log("console messages:\n" + (logs.join("\n") || "(none)"));
ws.close();