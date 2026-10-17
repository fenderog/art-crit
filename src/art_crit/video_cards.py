"""The text of `art-crit video`: each card is a small HTML page that headless Chrome screenshots to a PNG (ffmpeg here
has no `drawtext`). Everything that comes from a run or prompt goes through `esc()`; the pages have no scripts."""

from html import escape as esc

CSS = """
*{box-sizing:border-box;margin:0}
body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;position:relative;color:#f5f5f7;background:#0e0e13;
  font-family:-apple-system,"SF Pro Display","Helvetica Neue",Arial,sans-serif}
.brand{position:absolute;font-size:34px;font-weight:700;letter-spacing:.04em;color:#a99bff}
.clamp{display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
.pill{display:inline-block;padding:6px 22px;border-radius:999px;background:#a99bff;color:#14121f;font-weight:700}
.dim{color:#9a9aa6}
.abs{position:absolute}
"""


def page(size, body, css=""):
    w, h = size
    return f"<!doctype html><meta charset=utf-8><style>{CSS % {'w': w, 'h': h}}{css}</style><body>{body}</body>"


def metrics_line(info):
    return " · ".join(info["metrics"]) or "no metrics recorded"


def intro_card(size, title, prompt, n, kind):
    body = f"""
<div class=brand style="left:80px;top:90px">ART-CRIT</div>
<div class=abs style="left:80px;right:80px;top:300px;font-size:120px;font-weight:800;line-height:1.05">One prompt.<br>{esc(str(n))} answers.</div>
<div class="abs dim" style="left:80px;top:610px;font-size:40px">{esc(title)} · {esc(kind)}</div>
<div class="abs clamp" style="left:80px;right:80px;top:700px;font-size:54px;line-height:1.3;-webkit-line-clamp:9">{esc(prompt)}</div>"""
    return page(size, body)


def outro_card(size, url, n):
    body = f"""
<div class=brand style="left:80px;top:90px">ART-CRIT</div>
<div class=abs style="left:80px;right:80px;top:40%;font-size:96px;font-weight:800;line-height:1.1">Compare all {esc(str(n))} side by side</div>
<div class=abs style="left:80px;right:80px;top:calc(40% + 230px);font-size:40px;color:#a99bff">{esc(url)}</div>"""
    return page(size, body)


def run_card(layout, size, i, n, info, prompt):
    """The frame a run's picture is laid over: reveal = square picture between the prompt and the caption (vertical);
    wide = picture on the left, the caption in a panel on the right. Returns (html, picture x, picture y)."""
    counter = f"{i} / {n}"
    if layout == "wide":
        body = f"""
<div class="abs clamp dim" style="left:1140px;right:60px;top:60px;font-size:30px;line-height:1.35;-webkit-line-clamp:4">{esc(prompt)}</div>
<div class="abs dim" style="left:1140px;top:330px;font-size:34px">{esc(info['vendor'])}</div>
<div class="abs" style="left:1140px;right:60px;top:380px;font-size:72px;font-weight:800;line-height:1.05;word-break:break-word">{esc(info['name'])}</div>
<div class="abs" style="left:1140px;top:580px"><span class=pill style="font-size:40px">{esc(info['effort'])}</span></div>
<div class="abs dim" style="left:1140px;right:60px;top:700px;font-size:34px;line-height:1.5">{esc(metrics_line(info))}</div>
<div class=brand style="left:1140px;bottom:60px">ART-CRIT</div>
<div class="abs dim" style="right:60px;bottom:60px;font-size:34px">{counter}</div>"""
        return page(size, body), 0, 0
    body = f"""
<div class=brand style="left:60px;top:50px">ART-CRIT</div>
<div class="abs dim" style="right:60px;top:54px;font-size:34px">{counter}</div>
<div class="abs clamp" style="left:60px;right:60px;top:110px;font-size:40px;line-height:1.3;-webkit-line-clamp:4">{esc(prompt)}</div>
<div class="abs dim" style="left:60px;top:1415px;font-size:36px">{esc(info['vendor'])}</div>
<div class="abs" style="left:60px;right:60px;top:1465px;font-size:84px;font-weight:800;line-height:1.05;word-break:break-word">{esc(info['name'])}</div>
<div class="abs" style="left:60px;top:1640px"><span class=pill style="font-size:44px">{esc(info['effort'])}</span></div>
<div class="abs dim" style="left:60px;right:60px;top:1750px;font-size:36px">{esc(metrics_line(info))}</div>"""
    return page(size, body), 0, 300


def grid_card(size, title, prompt, infos, tiles, label_h, url):
    """The frame the pictures of every run are laid over (`tiles` = their (x, y, side) boxes, in order)."""
    labels = "".join(
        f"""<div class=abs style="left:{x}px;top:{y + side + 6}px;width:{side}px;height:{label_h}px;font-size:{26 if side < 400 else 30}px;line-height:1.15;overflow:hidden">
<b>{esc(info['name'])}</b> <span class=dim>{esc(info['effort'])}</span></div>"""
        for info, (x, y, side) in zip(infos, tiles))
    body = f"""
<div class=brand style="left:60px;top:50px">ART-CRIT</div>
<div class="abs dim" style="right:60px;top:54px;font-size:34px">{esc(title)}</div>
<div class="abs clamp" style="left:60px;right:60px;top:110px;font-size:44px;line-height:1.3;-webkit-line-clamp:4">{esc(prompt)}</div>
{labels}
<div class="abs dim" style="left:60px;right:60px;bottom:40px;font-size:30px;text-align:center">{esc(url)}</div>"""
    return page(size, body)
