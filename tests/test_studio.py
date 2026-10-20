"""The video studio: what a spec may hold, the timeline the preview and the render share, real renders from a fixture
site (ffmpeg + Chrome, no model), and the local-only API (GET api/studio, POST api/studio/plan, POST api/video, the job
list and the files)."""

import json
import time
import urllib.error
import urllib.request

import pytest

from art_crit import studio, video, video_sound
from art_crit.serve import serve_in_thread
from art_crit.util import CritError
from test_video import HIGH, OTHER, needs_tools, probe, site  # noqa: F401 (site is a fixture)
from test_web_kind import in_thread

ART = lambda run: {"page": "art", "run": run}  # noqa: E731


def card(type, at, secs=3, **kw):
    return {"id": f"{type}{at}", "type": type, "heading": kw.get("heading", "Hello"), "sub": "", "link": kw.get("link", ""),
            "look": "dark", "secs": secs, "at": at}


def test_the_catalog_matches_the_scene_and_the_page():
    c = studio.catalog()
    assert set(c["templates"]) == {"duel", "lineup", "wipe", "ladder", "countdown", "montage"}
    for t in c["templates"].values():
        assert t["format"] in studio.FORMATS and t["size"] == studio.FORMATS[t["format"]]
    assert {k for k, t in studio.TEMPLATES.items() if t["together"]} == set(studio.TILE_BOX)
    assert set(c["music"]) == {"none", *video_sound.STYLES}
    assert studio.slot_labels("lineup", 4) == ["1", "2", "3", "4"] and studio.slot_labels("lineup", 9) == ["1", "2", "3"]


def test_a_runs_type_and_length():
    still = {"kind": "media", "output": {"items": [{"type": "image"}]}}
    clip = {"kind": "media", "output": {"items": [{"type": "image"}, {"type": "video", "duration_s": 7.4}]}}
    assert [studio.slot_type(r) for r in (still, clip, {"kind": "godot", "output": {}}, {"kind": "web", "output": {}},
                                          {"kind": "blender", "output": {"items": [{"type": "model"}]}})] == ["image", "video", "game", "web", "model"]
    assert studio.clip_seconds(still, 5) == 5 and studio.clip_seconds(clip, 5) == 7.4
    assert studio.clip_seconds({"output": {"items": [{"type": "video", "duration_s": 40}]}}, 3) == 10  # capped
    assert studio.clip_seconds({"kind": "godot"}, 3) == studio.TYPES["game"]["secs"]


def test_a_bad_spec_is_refused_with_the_reason(site):  # noqa: F811
    good = {"template": "duel", "slots": [ART(HIGH), ART(OTHER)]}
    assert studio.check_spec(site, good)[0]["count"] == 2
    for patch, error in [
        ({"template": "nope"}, "template must be one of"),
        ({"slots": [ART(HIGH), ART(OTHER), ART(HIGH)]}, "has 2 slots"),
        ({"slots": [ART(HIGH)]}, "slot Right is empty"),
        ({"slots": [{"page": "../art", "run": HIGH}, None]}, "no such page"),
        ({"slots": [ART("nope"), None]}, "no such run"),
        ({"slots": [ART("model-x-low-20260102-000000"), None]}, "nothing to show"),
        ({"slots": ["x", None]}, "{page, run} or null"),
        ({"cards": [{**card("title", 0), "type": "poster"}]}, "card type"),
        ({"cards": [{**card("title", 0), "look": "neon"}]}, "look must be"),
        ({"cards": [card("title", 0, secs=4)]}, "a card's length"),
        ({"cards": [card("title", 0, heading="x" * 91)]}, "at most 90"),
        ({"cards": [card("title", -1)]}, "whole number"),
        ({"cards": [card("title", 0)] * 13}, "at most 12 cards"),
        ({"still": 7}, "seconds for a still"),
        ({"sync": "fast"}, "sync must be"),
        ({"music": "jazz"}, "music must be"),
        ({"labels": "yes"}, "true or false"),
        ({"wipe": 120}, "0 to 100"),
    ]:
        with pytest.raises(CritError, match=error.replace("{", r"\{").replace("}", r"\}")):
            studio.check_spec(site, {**good, **patch}, complete="slots" not in patch or "empty" in error)
    spec, runs = studio.check_spec(site, {"template": "duel", "slots": [ART(HIGH)]}, complete=False)  # the preview allows gaps
    assert runs[1] is None and spec["slots"][1] is None
    assert studio.check_spec(site, {**good, "cards": [card("title", 0, link="x")]})[0]["cards"][0]["link"] == ""  # only a vote card has one


def test_cards_go_between_the_results_in_play_order():
    run = {"kind": "media", "output": {"items": [{"type": "image"}]}}
    base = {"still": 2, "cards": []}
    together, total = studio.timeline({**base, "template": "duel", "cards": [card("vote", 99), card("title", 0)]}, [run, run])
    assert [(s["type"], s.get("card")) for s in together] == [("card", "title0"), ("slots", None), ("card", "vote99")]
    assert [s["start"] for s in together] == [0, 3, 5] and total == 8
    one_by_one, total = studio.timeline({**base, "template": "ladder", "cards": [card("section", 2, secs=5), card("title", 0)]}, [run, None, run, run])
    assert [s.get("slot", s.get("card")) for s in one_by_one] == ["title0", 0, 1, "section2", 2, 3]
    assert total == 3 + 4 * 2 + 5  # an empty slot counts as a still in the preview


def test_the_sound_cues_follow_the_segments():
    plan = {"timing": video.TIMING, "metrics": True, "slots": [{}, {}], "segments": [
        {"type": "card", "start": 0, "frames": 60, "card": {"link": "x"}},
        {"type": "slot", "start": 60, "frames": 60, "slot": 0}, {"type": "slot", "start": 120, "frames": 60, "slot": 1}]}
    cues = studio.cues(plan)
    assert sum(k == "whoosh" for _, k in cues) == 2 and sum(k == "pop" for _, k in cues) == 4
    assert any(k == "tick" for _, k in cues) and all(at < 6 for at, _ in cues)


@needs_tools
@pytest.mark.parametrize("template, slots, cards, size", [
    ("duel", [ART(HIGH), ART(OTHER)], [card("title", 0, secs=2), card("vote", 99, secs=2, link="fenderog.com/art-crit")], (1920, 1080)),
    ("ladder", [ART(HIGH), ART(OTHER), ART(HIGH), ART(OTHER)], [card("section", 2, secs=2)], (1080, 1920)),  # a run twice: recorded once
])
def test_a_template_renders_at_its_format_and_length(site, tmp_path, template, slots, cards, size):  # noqa: F811
    spec = {"template": template, "slots": slots, "cards": cards, "still": 2, "music": "lofi", "metrics": True}
    said = []
    out = in_thread(studio.make_studio_video, site, spec, tmp_path, said.append)
    width, height, seconds = probe(out)
    checked, runs = studio.check_spec(site, spec)
    assert (width, height) == size and seconds == pytest.approx(studio.timeline(checked, runs)[1], abs=0.2)
    assert sum("recording" in s for s in said) == 2


@needs_tools
def test_text_on_a_card_never_becomes_markup(site, tmp_path):  # noqa: F811
    """The studio scene puts card text in with textContent: a heading full of tags draws as text."""
    def render():
        spec, runs = studio.check_spec(site, {"template": "duel", "slots": [ART(HIGH), ART(OTHER)],
                                              "cards": [card("title", 0, heading='<img src=x onerror="document.title=1"><b id=evil>')]})
        work = tmp_path / "work"
        work.mkdir()
        with video.studio(site / "docs", work) as chrome:
            clips = [video.extract_frames(video.make_source(chrome, site / "docs", "art", r, 2, work, print), work / "clips" / str(n)) for n, r in enumerate(runs)]
            (work / "plan-studio.json").write_text(json.dumps(studio.scene_plan(spec, runs, clips)))
            tab = chrome.renderer.new_page(viewport={"width": 1920, "height": 1080})
            tab.goto(f"{chrome.scene}/studio.html?plan=plan-studio.json")
            tab.wait_for_function("() => window.sceneReady === true")
            tab.evaluate("(f) => window.renderFrame(f)", 30)
            return tab.evaluate("() => [document.getElementById('evil'), document.title, document.body.textContent.includes('<b id=evil>')]")
    assert in_thread(render) == [None, "art-crit video scene", True]


# --- the local API -------------------------------------------------------------------------------------------------

def call(base, path, body=None, headers=None):
    request = urllib.request.Request(base + path, method="POST" if body is not None else "GET", headers={"Content-Type": "application/json", **(headers or {})},
                                     data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(request) as res:
            return res.status, res.read(), res.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


@pytest.fixture
def api(site):  # noqa: F811
    server = serve_in_thread(site / "docs")
    yield f"http://127.0.0.1:{server.server_address[1]}/", server.server_address[1]
    server.shutdown()
    server.server_close()


def test_the_api_offers_the_catalog_and_the_previews_timeline(api):
    base, _ = api
    status, out, headers = call(base, "api/studio")
    assert status == 200 and json.loads(out)["templates"]["duel"]["name"] == "Head to head"
    assert "Access-Control-Allow-Origin" not in headers
    status, out, headers = call(base, "api/studio/plan", {"template": "duel", "slots": [ART(HIGH), None], "cards": [card("title", 0)]})
    plan = json.loads(out)
    assert status == 200 and [s["type"] for s in plan["segments"]] == ["card", "slots"] and plan["total"] == 6
    assert plan["slots"] == [{"type": "video", "secs": 2}, None]  # the fixture run has a short video (played at least 2 s) and plan["labels"] == ["Left", "Right"]
    assert "Access-Control-Allow-Origin" not in headers
    status, out, _ = call(base, "api/studio/plan", {"template": "nope"})
    assert status == 400 and "template" in json.loads(out)["error"]


@needs_tools
def test_the_api_renders_in_the_background_and_serves_only_its_files(api, site):  # noqa: F811
    base, _ = api
    assert json.loads(call(base, "api/local")[1])["video"] is True
    for body, error in [({"runs": [HIGH]}, "expected {studio: spec}"), ({"studio": {"template": "duel", "slots": [ART(HIGH)]}}, "is empty")]:
        status, out, _ = call(base, "api/video", body)
        assert status == 400 and error in json.loads(out)["error"]
    spec = {"template": "duel", "slots": [ART(HIGH), ART(OTHER)], "cards": [card("title", 0, secs=2, heading="Robots")], "still": 2, "music": "none"}
    status, out, _ = call(base, "api/video", {"studio": spec})
    assert status == 200
    job = json.loads(out)["job"]
    assert call(base, "api/video", {"studio": spec})[0] == 400  # one at a time
    for _ in range(240):
        state = json.loads(call(base, f"api/video?job={job}")[1])
        if state["state"] != "running":
            break
        time.sleep(0.5)
    assert state["state"] == "done" and len(state["files"]) == 1, state
    assert (state["title"], state["template"], state["format"], state["slots"], state["length"]) == ("Robots", "Head to head", "16:9", 2, 4)
    assert [j["job"] for j in json.loads(call(base, "api/video/jobs")[1])["jobs"]][0] == job
    status, data, headers = call(base, f"api/video/file?job={job}&name={state['files'][0]}")
    assert status == 200 and headers["Content-Type"] == "video/mp4" and b"ftyp" in data[:32]
    assert "Access-Control-Allow-Origin" not in headers  # another website can't read it
    for name in ("../../docs/index.html", "page.json", ""):
        assert call(base, f"api/video/file?job={job}&name={name}")[0] == 404
    assert (site / "videos/studio" / state["files"][0]).is_file()  # outside docs/: never published
    assert call(base, "api/video?job=nope")[0] == 404


def test_the_api_refuses_other_hosts_and_other_sites(api, site):  # noqa: F811
    base, port = api
    spec = {"studio": {"template": "duel", "slots": [ART(HIGH), ART(OTHER)]}}
    evil = {"Host": f"evil.example:{port}", "Origin": f"http://evil.example:{port}"}
    assert call(base, "api/video", spec, evil)[0] == 403
    assert call(base, "api/studio/plan", spec["studio"], evil)[0] == 403
    for path in ("api/video?job=x", "api/video/jobs", "api/studio"):
        assert call(base, path, None, {"Host": f"evil.example:{port}"})[0] == 403
    assert call(base, "api/video", spec, {"Origin": "https://evil.example"})[0] == 403
    req = urllib.request.Request(base + "api/video", method="POST", data=b"{}", headers={"Content-Type": "text/plain"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req)
    assert e.value.code == 415
    assert not (site / "videos").exists()
