"""Build the static Pages upload from docs/, compressing engines for the path router.

Run from the repo root: python3 cloudflare/prepare.py. No packages required.
"""

import gzip
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 25 * 1024 * 1024


def prepare(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    for wasm in destination.glob("engines/*/godot.wasm"):
        compressed = wasm.with_suffix(".wasm.gz")
        with wasm.open("rb") as original, compressed.open("wb") as target:
            # No embedded filename or timestamp: identical builds upload identical bytes.
            with gzip.GzipFile(fileobj=target, mode="wb", filename="", mtime=0, compresslevel=9) as output:
                shutil.copyfileobj(original, output)
        if compressed.stat().st_size > LIMIT:
            raise ValueError(f"compressed engine still exceeds Pages' 25 MiB limit: {wasm}")
        wasm.unlink()
    oversized = [str(p) for p in destination.rglob("*") if p.is_file() and p.stat().st_size > LIMIT]
    if oversized:
        raise ValueError(f"Pages assets exceed 25 MiB: {', '.join(oversized)}")


if __name__ == "__main__":
    prepare(ROOT / "docs", ROOT / "cloudflare-dist")
    print("Prepared cloudflare-dist/ for Pages")
