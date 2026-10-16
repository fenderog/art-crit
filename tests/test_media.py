"""media.normalize: checking and normalizing the files a media run left in ./output/.
Inputs are generated with ffmpeg, so the module is skipped without it."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from art_crit.kinds import media

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="needs ffmpeg")


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, args)], check=True)


@pytest.fixture
def out(tmp_path):
    (tmp_path / "lvl" / "output").mkdir(parents=True)
    return tmp_path / "lvl" / "output"


def finalize(out):
    return media.normalize(out.parent, out.parent.parent / "media")


def test_valid_image_svg_and_video(out):
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=64x48", "-frames:v", "1", out / "a.png")
    (out / "b.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="30px" height="20"/>')
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=160x120:rate=10", "-t", "2", "-c:v", "libx264", "-pix_fmt", "yuv420p", out / "c.mp4")
    m = finalize(out)
    assert m["ok"] and not m["errors"]
    a, b, c = m["items"]
    assert (a["type"], a["width"], a["height"]) == ("image", 64, 48)
    assert (b["type"], b["width"], b["height"]) == ("image", 30, 20)
    assert c["type"] == "video" and not c["transcoded"] and c["poster"] == "c.poster.jpg"
    written = out.parent.parent / "media"
    assert json.loads((written / "manifest.json").read_text()) == m
    assert {p.name for p in written.iterdir()} == {"a.png", "b.svg", "c.mp4", "c.poster.jpg", "manifest.json"}


def test_long_webm_is_trimmed_and_reencoded_to_mp4(out):
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=320x240:rate=10", "-t", "12", out / "clip.webm")
    [item] = finalize(out)["items"]
    assert item["file"] == "clip.mp4" and item["transcoded"] and item["trimmed"]
    assert item["duration_s"] <= media.MAX_VIDEO_S
    info = media.probe(out.parent.parent / "media" / "clip.mp4")
    assert info["codec"] == "h264" and info["duration"] <= media.MAX_VIDEO_S + 0.1


def test_bad_files_become_errors_and_ok_is_false(out):
    (out / "fake.png").write_bytes(b"not a png")
    (out / "notes.txt").write_text("hello")  # not media: skipped, not an error
    (out / "broken.svg").write_text("<svg")
    m = finalize(out)
    assert not m["ok"] and m["items"] == []
    assert m["errors"] == ["broken.svg: not a valid SVG", "fake.png: not a readable image"]
    assert not (out.parent.parent / "media" / "notes.txt").exists()


def test_output_without_any_media_file_is_an_error(out):
    (out / "make.py").write_text("print('hi')\n")
    m = finalize(out)
    assert not m["ok"] and m["items"] == []
    assert m["errors"] == ["no image or video files in ./output/"]


def test_stray_non_media_file_does_not_fail_a_good_output(out):
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=64x48", "-frames:v", "1", out / "a.png")
    (out / "make.py").write_text("print('hi')\n")
    m = finalize(out)
    assert m["ok"] and m["errors"] == []
    assert [i["file"] for i in m["items"]] == ["a.png"]
    assert not (out.parent.parent / "media" / "make.py").exists()


def test_keep_source_takes_a_script_left_in_output_but_no_media_file(out):
    kind = media.Media()
    (out / "make.py").write_text("print('hi')\n")
    (out / "drawing.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>')
    (out.parent / "make.py").write_text("print('hi')\n")
    assert kind.keep_source(Path("make.py"), out.parent / "make.py")
    assert kind.keep_source(Path("output/make.py"), out / "make.py")
    assert not kind.keep_source(Path("output/drawing.svg"), out / "drawing.svg")


def test_empty_output_and_too_many_files(out, monkeypatch):
    assert finalize(out)["errors"] == ["no files in ./output/"]
    monkeypatch.setattr(media, "MAX_FILES", 2)
    for name in "abc":
        (out / f"{name}.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>')
    m = finalize(out)
    assert len(m["items"]) == 2 and "only the first 2" in m["errors"][0]


def test_oversized_png_becomes_jpeg(out, monkeypatch):
    ffmpeg("-f", "lavfi", "-i", "mandelbrot=s=320x240", "-frames:v", "1", out / "big.png")  # ~66 KB png, ~23 KB jpeg
    monkeypatch.setattr(media, "MAX_BYTES", 40_000)
    [item] = finalize(out)["items"]
    assert item["file"] == "big.jpg" and item["width"] == 320 and item["bytes"] <= 40_000


def test_name_collisions_are_reported_not_overwritten(out):
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=160x120:rate=10", "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p", out / "x.mp4")
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=160x120:rate=10", "-t", "1", out / "x.webm")
    m = finalize(out)
    assert [i["file"] for i in m["items"]] == ["x.mp4"]
    assert m["errors"] == ["x.webm: skipped, another output is already named x.mp4"]


def test_thumbnail_is_a_small_jpeg_with_transparency_over_white(tmp_path):
    src = tmp_path / "t.png"
    ffmpeg("-f", "lavfi", "-i", "color=c=red@0.0:s=1200x900,format=rgba", "-frames:v", "1", src)
    assert media.write_thumb(src, tmp_path / "out" / "t.thumb.jpg")  # makes the parent dir
    out = tmp_path / "out" / "t.thumb.jpg"
    assert out.read_bytes()[:2] == b"\xff\xd8"
    info = media.probe(out)
    assert (info["width"], info["height"]) == (800, 600)  # at most THUMB_WIDTH wide, aspect kept
    pixels = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-vf", "crop=2:2:0:0", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
                            capture_output=True, check=True).stdout
    assert set(pixels) == {255}  # transparent pixels are white, not black
    assert not media.write_thumb(tmp_path / "missing.png", tmp_path / "x.jpg")
    (tmp_path / "bad.png").write_bytes(b"not a png")
    assert not media.write_thumb(tmp_path / "bad.png", tmp_path / "x.jpg")


def test_add_thumbs_gives_items_thumbnails_and_picks_the_runs(tmp_path):
    run_dir = tmp_path / "run"
    (run_dir / "media").mkdir(parents=True)
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=64x48", "-frames:v", "1", run_dir / "media/a.png")
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=64x48", "-frames:v", "1", run_dir / "media/a.jpg")  # same stem: no name left
    ffmpeg("-f", "lavfi", "-i", "testsrc=size=64x48", "-frames:v", "1", run_dir / "media/clip.poster.jpg")
    (run_dir / "media/d.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    items = [
        {"type": "image", "path": "media/d.svg"},
        {"type": "video", "path": "media/clip.mp4", "poster": "media/clip.poster.jpg"},
        {"type": "image", "path": "media/a.png"},
        {"type": "image", "path": "media/a.jpg"},
        {"type": "model", "path": "media/m.glb"},
    ]
    assert media.add_thumbs(run_dir, items) == "media/clip.thumb.jpg"  # the first item's thumb: the SVG has none
    assert [i.get("thumb") for i in items] == [None, "media/clip.thumb.jpg", "media/a.thumb.jpg", None, None]
    assert (run_dir / "media/a.thumb.jpg").is_file() and (run_dir / "media/clip.thumb.jpg").is_file()
    # idempotent: a second pass makes nothing new and keeps the thumbs
    before = sorted(p.name for p in (run_dir / "media").iterdir())
    assert media.add_thumbs(run_dir, items) == "media/clip.thumb.jpg"
    assert sorted(p.name for p in (run_dir / "media").iterdir()) == before
    # no thumbnail at all (SVG only): the first image as is
    assert media.add_thumbs(run_dir, [{"type": "image", "path": "media/d.svg"}]) == "media/d.svg"
