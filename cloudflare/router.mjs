// Only /art-crit is routed here. The Pages project holds the static files;
// large Godot engines are stored there as .wasm.gz (Pages caps assets at 25 MiB).
const PAGES = "https://art-crit.pages.dev";
const ENGINE = /^\/engines\/[a-f0-9]{12}\/godot\.wasm$/;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/art-crit") {
      url.pathname += "/";
      return Response.redirect(url.toString(), 308);
    }
    if (!url.pathname.startsWith("/art-crit/")) return new Response("Not found", { status: 404 });
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405 });
    }

    const path = url.pathname.slice("/art-crit".length);
    const upstream = new URL(PAGES);
    upstream.pathname = ENGINE.test(path) ? `${path}.gz` : path;
    upstream.search = url.search;
    // Keep Range for Safari video playback; never forward cookies or credentials.
    const headers = new Headers();
    if (!ENGINE.test(path)) {
      for (const name of ["Range", "If-Range"]) {
        if (request.headers.has(name)) headers.set(name, request.headers.get(name));
      }
    }
    const response = await fetch(upstream.toString(), { headers });
    if (!ENGINE.test(path)) {
      // Pages currently ignores Range on MP4s. Our normalized videos are ≤2 MiB;
      // synthesize a partial response for Safari without buffering larger assets.
      const range = request.headers.get("Range");
      if (request.method === "GET" && range && response.status === 200 &&
          response.headers.get("Content-Type")?.startsWith("video/")) {
        const length = Number(response.headers.get("Content-Length"));
        if (length > 0 && length <= 2 * 1024 * 1024 &&
            (!request.headers.has("If-Range") || request.headers.get("If-Range") === response.headers.get("ETag"))) {
          const match = /^bytes=(\d*)-(\d*)$/.exec(range);
          if (match && (match[1] || match[2])) {
            const start = match[1] ? Number(match[1]) : Math.max(0, length - Number(match[2]));
            const end = match[1] ? (match[2] ? Math.min(Number(match[2]), length - 1) : length - 1) : length - 1;
            if (start >= length || end < start) {
              return new Response(null, { status: 416, headers: { "Content-Range": `bytes */${length}` } });
            }
            const bytes = await response.arrayBuffer();
            const partialHeaders = new Headers(response.headers);
            partialHeaders.set("Content-Range", `bytes ${start}-${end}/${length}`);
            partialHeaders.set("Content-Length", String(end - start + 1));
            partialHeaders.set("Accept-Ranges", "bytes");
            return new Response(bytes.slice(start, end + 1), { status: 206, headers: partialHeaders });
          }
        }
      }
      return response;
    }
    if (response.status !== 200) return response;
    const wasmHeaders = new Headers({
      "Content-Type": "application/wasm",
      "Access-Control-Allow-Origin": "*", // sandboxed game frames have opaque origins
      "Cache-Control": "public, max-age=31536000, immutable", // hashed engine directory
    });
    if (request.method === "HEAD") return new Response(null, { status: 200, headers: wasmHeaders });
    return new Response(response.body.pipeThrough(new DecompressionStream("gzip")), { status: 200, headers: wasmHeaders });
  },
};
