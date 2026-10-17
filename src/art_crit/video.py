"""`art-crit video`: social-media videos that compare some runs of a page, made on this machine with ffmpeg and headless
Chrome (never published: they go to <root>/videos/, outside docs/). SPEC.md "Social videos", ADR-0032.

Every run becomes one silent 1080x1080 source clip (`make_source`): its video, a turntable of its 3D model, a recording of
its game or page, or its pictures with a slow zoom. Each requested layout lays the sources over text cards
(`video_cards`, screenshotted by Chrome because ffmpeg here has no drawtext) and joins the segments."""

import contextlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from . import video_cards as cards
from .site import run_failed
from .util import CritError

SITE_URL = "https://fenderog.com/art-crit/"
SITE_NAME = "fenderog.com/art-crit"  # what the cards say; the compare link is for the post (`compare_url`)
SIDE = 1080  # every source clip is SIDE x SIDE
FPS = 30
BG = "0x0e0e13"
LAYOUTS = {"reveal": (1080, 1920), "grid": (1080, 1920), "wide": (1920, 1080)}
LAYOUT_NAMES = {"reveal": "Vertical, one at a time", "grid": "Vertical, all at once", "wide": "Landscape, one at a time"}
MAX_RUNS = 12
INTRO_S, OUTRO_S, FADE_S = 2.2, 2.2, 0.25
ENCODE = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]
MAX_IMAGES = 3


def ffmpeg(*args):
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        raise CritError(f"ffmpeg failed: {r.stderr.strip()[-500:]}")


def join(parts, out, *extra):
    """Concatenate clips that were encoded alike without re-encoding them (plus `extra` output options)."""
    listing = Path(parts[0]).with_name(f"{Path(out).stem}-parts.txt")
    listing.write_text("".join(f"file '{p}'\n" for p in parts))
    ffmpeg("-f", "concat", "-safe", "0", "-i", listing, *extra, "-c:v", "copy", out)


def fit(side=SIDE):
    """The filter that fits a picture into a side x side square on the background colour."""
    return f"scale={side}:{side}:force_original_aspect_ratio=decrease,pad={side}:{side}:(ow-iw)/2:(oh-ih)/2:color={BG},setsar=1"


def pad2(n):
    return f"{n:.2f}"


# ---- headless Chrome ------------------------------------------------------------------------------------------------

class Studio:
    """The site served from docs/ and one Chrome, which screenshots cards and records games."""

    def __init__(self, origin, browser):
        self.origin, self.browser = origin, browser

    def screenshot(self, html, size, out):
        """A card (HTML with no scripts) or a picture page, as a PNG of exactly `size`."""
        context = self.browser.new_context(viewport={"width": size[0], "height": size[1]}, java_script_enabled=False)
        try:
            page = context.new_page()
            page.set_content(html)
            page.screenshot(path=str(out))
        finally:
            context.close()


@contextlib.contextmanager
def studio(docs):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise CritError("videos need Playwright and Chrome: uv tool install --editable '.[verify]' (see the README)")
    from .serve import serve_in_thread

    server = serve_in_thread(docs)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", args=["--enable-unsafe-swiftshader", "--use-angle=swiftshader"])
            try:
                yield Studio(f"http://127.0.0.1:{server.server_address[1]}", browser)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


def record(studio, url, prepare, act, work, size=(1080, 1200)):
    """Open `url` in a page that is being recorded; `prepare(page)` waits until the picture is up and returns its
    bounding box, `act(page, box)` runs for the clip's length. Returns (the .webm, box); the clip is its last seconds."""
    context = studio.browser.new_context(viewport={"width": size[0], "height": size[1]}, record_video_dir=str(work),
                                         record_video_size={"width": size[0], "height": size[1]})
    try:
        page = context.new_page()
        page.goto(url)
        box = prepare(page)
        act(page, box)
    finally:
        context.close()
    return Path(page.video.path()), box


def crop_filter(box, size):
    """Crop to the recorded element's box (even sizes, inside the viewport), then fit the square."""
    x, y = max(0, int(box["x"])), max(0, int(box["y"]))
    w, h = min(int(box["width"]), size[0] - x) // 2 * 2, min(int(box["height"]), size[1] - y) // 2 * 2
    return f"crop={w}:{h}:{x}:{y},fps={FPS},{fit()}"


def record_game(studio, slug, run, seconds, work):
    """A game or page, in the same sandbox as the site (play.html), played a little: a click, then a few key presses."""
    size = (1080, 1200)

    def prepare(page):
        frame = page.locator(".play-frame iframe")
        frame.wait_for(timeout=30000)
        page.wait_for_timeout(4000)  # booting
        box = frame.bounding_box()
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        return box

    def act(page, box):
        keys = ["ArrowRight", "Space", "ArrowLeft", "ArrowUp", "Space", "ArrowDown"]
        for i in range(int(seconds * 2)):
            page.keyboard.press(keys[i % len(keys)])
            page.wait_for_timeout(500)

    url = f"{studio.origin}/play.html?p={quote(slug)}&r={quote(run['id'])}"
    return _recorded_clip(studio, url, prepare, act, work, size, seconds)


def record_model(studio, slug, run, seconds, work):
    """A 3D model: the run page's viewer, orbited back and forth with the mouse."""
    size = (1080, 1300)

    def prepare(page):
        page.locator(".model-view .play-overlay").first.click(timeout=30000)
        stage = page.locator(".model-stage[data-loaded=true]")
        stage.wait_for(timeout=45000)
        page.evaluate("() => document.querySelectorAll('.model-hint').forEach((n) => n.remove())")  # "drag to orbit"
        box = stage.locator("canvas").bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.wheel(0, -250)  # a little closer: models are framed with room to spare
        page.wait_for_timeout(500)
        return box

    def act(page, box):
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        page.mouse.move(cx - 150, cy)
        page.mouse.down()
        steps = int(seconds * 20)
        for i in range(steps):
            page.mouse.move(cx - 150 + 300 * i / steps, cy)
            page.wait_for_timeout(50)
        page.mouse.up()

    url = f"{studio.origin}/run.html?p={quote(slug)}&r={quote(run['id'])}"
    return _recorded_clip(studio, url, prepare, act, work, size, seconds)


def _recorded_clip(studio, url, prepare, act, work, size, seconds):
    video, box = record(studio, url, prepare, act, work, size)
    out = Path(work) / f"{video.stem}.mp4"
    # the recording starts at page creation: the clip is the end of it, after the booting and the first click
    ffmpeg("-sseof", f"-{seconds}", "-i", video, "-t", seconds, "-vf", f"{crop_filter(box, size)},tpad=stop_mode=clone:stop_duration={seconds}", *ENCODE, out)
    return out


# ---- one source clip per run ----------------------------------------------------------------------------------------

def still_clip(image, frames, out):
    """A picture held for `frames` frames with a slow zoom in (drawn on a 2x canvas so the zoom doesn't jitter)."""
    big = SIDE * 2
    zoom = f"zoompan=z='min(1+0.0005*on,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={SIDE}x{SIDE}:fps={FPS}"
    ffmpeg("-i", image, "-vf", f"{fit(big)},{zoom},format=yuv420p", "-frames:v", frames, *ENCODE, out)


def video_clip(path, seconds, out):
    ffmpeg("-i", path, "-vf", f"fps={FPS},{fit()},tpad=stop_mode=clone:stop_duration={seconds}", "-t", seconds, *ENCODE, out)


def items_of(run):
    return (run.get("output") or {}).get("items") or []


def pictures(run, run_dir):
    """The run's image items as paths, the owner's thumbnail pick (if it is one of them) first."""
    images = [i for i in items_of(run) if i["type"] == "image"]
    images.sort(key=lambda i: run.get("thumb") not in (i["path"], i.get("thumb")))
    return [run_dir / i["path"] for i in images[:MAX_IMAGES]]


def make_source(studio, docs, slug, run, seconds, work, say):
    """One silent SIDE x SIDE clip of `seconds` that shows the run, or None when there is nothing to show."""
    run_dir = docs / "data" / slug / "runs" / run["id"]
    out = Path(work) / f"{run['id']}.mp4"
    items = items_of(run)
    try:
        if not items:  # a game or page
            return record_game(studio, slug, run, seconds, work)
        video = next((i for i in items if i["type"] == "video"), None)
        if video:
            video_clip(run_dir / video["path"], seconds, out)
            return out
        if any(i["type"] == "model" for i in items):
            return record_model(studio, slug, run, seconds, work)
    except Exception as e:  # a game that won't boot, a model that won't load: fall back to its pictures
        say(f"{run['id']}: recording failed ({str(e).splitlines()[0][:120]}); using its pictures")
        if not items:
            thumb = run.get("thumb")
            return _thumb_clip(run_dir, thumb, seconds, out)
    images = pictures(run, run_dir)
    if not images:
        return None
    frames = max(1, round(seconds * FPS / len(images)))
    parts = []
    for n, image in enumerate(images):
        if image.suffix.lower() == ".svg":  # only ever through <img>, in Chrome (ADR-0004); ffmpeg can't read SVG
            png = Path(work) / f"{run['id']}-{n}.png"
            rel = quote(str(image.relative_to(docs)))
            studio.screenshot(f'<body style="margin:0;background:#fff"><img src="{studio.origin}/{rel}" '
                              'style="width:100vw;height:100vh;object-fit:contain">', (SIDE, SIDE), png)
            image = png
        part = Path(work) / f"{run['id']}-{n}.mp4"
        still_clip(image, frames, part)
        parts.append(part)
    if len(parts) > 1:
        join(parts, out)
    else:
        shutil.move(parts[0], out)
    return out


def _thumb_clip(run_dir, thumb, seconds, out):
    if not thumb or not (run_dir / thumb).is_file():
        return None
    still_clip(run_dir / thumb, round(seconds * FPS), out)
    return out


# ---- text and layouts -----------------------------------------------------------------------------------------------

def run_info(run):
    """What a caption says about a run."""
    model = run["model"].split("@")[0]
    parts = model.split("/")
    vendor = parts[1] if parts[0] == "openrouter" and len(parts) > 2 else parts[0] if len(parts) > 1 else ""
    m = run.get("metrics") or {}
    cost = m.get("cost_usd") or 0
    metrics = []
    if m.get("duration_ms"):
        s = round(m["duration_ms"] / 1000)
        metrics.append(f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s")
    if m.get("tokens_total"):
        metrics.append(f"{m['tokens_total'] / 1000:.0f}k tokens" if m["tokens_total"] >= 1000 else f"{m['tokens_total']} tokens")
    if cost > 0:
        metrics.append(f"${cost:.2f}" if cost >= 0.01 else f"${cost:.3f}")
    return {"vendor": vendor, "name": parts[-1], "effort": run["effort"], "metrics": metrics}


def grid_tiles(n):
    """(boxes (x, y, side) of the n tiles, label height) for the vertical grid: 2 columns up to 6 runs, else 3."""
    width, height = LAYOUTS["grid"]
    top, bottom, label, gap = 300, 110, 64, 24
    cols = 2 if n <= 6 else 3
    rows = -(-n // cols)
    side = min((width - gap * (cols + 1)) // cols, (height - top - bottom - rows * label - gap * (rows + 1)) // rows) // 2 * 2
    x0 = (width - (cols * side + (cols - 1) * gap)) // 2
    y0 = top + (height - top - bottom - (rows * (side + label) + (rows - 1) * gap)) // 2
    return [(x0 + (i % cols) * (side + gap), y0 + (i // cols) * (side + label + gap), side) for i in range(n)], label


def card_segment(card, seconds, out):
    ffmpeg("-loop", 1, "-framerate", FPS, "-t", seconds, "-i", card,
           "-vf", f"fade=t=in:st=0:d={FADE_S},fade=t=out:st={pad2(seconds - FADE_S)}:d={FADE_S},format=yuv420p", *ENCODE, out)


def overlay_segment(card, placed, seconds, out):
    """The card with each (source clip, x, y, side) laid on it for `seconds`."""
    inputs = ["-loop", 1, "-framerate", FPS, "-t", seconds, "-i", card]
    chain, last = [], "0:v"
    for n, (clip, x, y, side) in enumerate(placed, 1):
        inputs += ["-i", clip]
        chain.append(f"[{n}:v]scale={side}:{side}[s{n}];[{last}][s{n}]overlay={x}:{y}:shortest=1[o{n}]")
        last = f"o{n}"
    chain.append(f"[{last}]fade=t=in:st=0:d={FADE_S},fade=t=out:st={pad2(seconds - FADE_S)}:d={FADE_S},format=yuv420p[v]")
    ffmpeg(*inputs, "-filter_complex", ";".join(chain), "-map", "[v]", "-t", seconds, *ENCODE, out)


def compose(studio, layout, page, runs, sources, seconds, work, out):
    size = LAYOUTS[layout]
    prompt = page.get("prompt") or page["title"]
    infos = [run_info(r) for r in runs]
    base = Path(work) / layout
    base.mkdir()
    parts = []

    def card_clip(name, html, secs):
        png = base / f"{name}.png"
        studio.screenshot(html, size, png)
        part = base / f"{name}.mp4"
        card_segment(png, secs, part)
        parts.append(part)

    card_clip("intro", cards.intro_card(size, page["title"], prompt, len(runs), page["kind"]), INTRO_S)
    if layout == "grid":
        tiles, label = grid_tiles(len(runs))
        png = base / "grid.png"
        studio.screenshot(cards.grid_card(size, page["title"], prompt, infos, tiles, label, SITE_NAME), size, png)
        part = base / "grid.mp4"
        overlay_segment(png, [(src, x, y, side) for src, (x, y, side) in zip(sources, tiles)], seconds, part)
        parts.append(part)
    else:
        for i, (info, src) in enumerate(zip(infos, sources), 1):
            html, x, y = cards.run_card(layout, size, i, len(runs), info, prompt)
            png = base / f"run-{i}.png"
            studio.screenshot(html, size, png)
            part = base / f"run-{i}.mp4"
            overlay_segment(png, [(src, x, y, SIDE)], seconds, part)
            parts.append(part)
    card_clip("outro", cards.outro_card(size, SITE_NAME, len(runs)), OUTRO_S)
    # social platforms like a sound track: add a silent one
    join(parts, out, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:a", "aac", "-movflags", "+faststart")


def compare_url(slug, run_ids):
    """The site's compare page for these runs: the link to put in the post."""
    return f"{SITE_URL}compare.html?p={quote(slug)}&r={quote(','.join(run_ids))}"


# ---- entry point ----------------------------------------------------------------------------------------------------

def check_request(root, slug, run_ids, layouts, seconds):
    """(page.json, the chosen runs in order, the layouts) or a CritError; nothing is started."""
    path = root / "docs" / "data" / slug / "page.json"
    if not path.is_file():
        raise CritError(f"no such page: {slug}")
    page = json.loads(path.read_text())
    by_id = {r["id"]: r for r in page["runs"]}
    for run_id in run_ids:
        if run_id not in by_id:
            raise CritError(f"no such run: {slug}/{run_id}")
    run_ids = list(dict.fromkeys(run_ids))
    if not 2 <= len(run_ids) <= MAX_RUNS:
        raise CritError(f"a video compares 2 to {MAX_RUNS} runs, got {len(run_ids)}")
    runs = [by_id[i] for i in run_ids]
    failed = [r["id"] for r in runs if run_failed(r)]
    if failed:
        raise CritError(f"failed runs have nothing to show: {', '.join(failed)}")
    layouts = list(dict.fromkeys(layouts or LAYOUTS))
    for layout in layouts:
        if layout not in LAYOUTS:
            raise CritError(f"unknown layout {layout!r} (expected one of: {', '.join(LAYOUTS)})")
    if not 2 <= seconds <= 20:
        raise CritError("seconds per run must be between 2 and 20")
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise CritError(f"videos need {tool} on PATH")
    return page, runs, layouts


def make_videos(root, slug, run_ids, layouts=None, seconds=6, out_dir=None, say=print):
    """Make one video per layout of the given runs of a page; returns the files (in <root>/videos/<slug>/ by default)."""
    page, runs, layouts = check_request(root, slug, run_ids, layouts, seconds)
    docs = root / "docs"
    out_dir = Path(out_dir) if out_dir else root / "videos" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    files = []
    with tempfile.TemporaryDirectory(prefix="art-crit-video-") as work, studio(docs) as chrome:
        sources = []
        for n, run in enumerate(runs, 1):
            say(f"recording {n}/{len(runs)}: {run['model']} {run['effort']}")
            source = make_source(chrome, docs, slug, run, seconds, work, say)
            if source is None:
                raise CritError(f"{run['id']} has no picture, video or model to show")
            sources.append(source)
        for layout in layouts:
            say(f"composing {layout} ({LAYOUT_NAMES[layout]})")
            out = out_dir / f"{stamp}-{slug}-{layout}.mp4"
            compose(chrome, layout, page, runs, sources, seconds, work, out)
            files.append(out)
    return files
