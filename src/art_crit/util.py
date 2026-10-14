"""Small shared helpers: the expected-error type, ids, slugs, timestamps."""

import re
from datetime import datetime, timezone


class CritError(Exception):
    """A user-facing error: printed to stderr without a traceback."""


# The full effort-level order a harness may report; used to sort/validate/expand -m LEVELS specs.
LEVEL_ORDER = ["off", "minimal", "low", "medium", "high", "xhigh", "max"]
LEVEL_INDEX = {level: i for i, level in enumerate(LEVEL_ORDER)}


def parse_duration(text):
    """'30m' / '90s' / '1h' -> seconds."""
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([smh])", str(text).strip())
    if not m:
        raise CritError(f"bad duration: {text!r} (expected e.g. 30m, 90s, 1h)")
    n, unit = float(m.group(1)), m.group(2)
    return n * {"s": 1, "m": 60, "h": 3600}[unit]


def expand_levels(spec, supported, model):
    """spec: 'all' | 'off' | 'a..b' | 'a,b,c'. supported: this model's levels, in LEVEL_ORDER.
    Raises CritError naming the supported levels when a requested one isn't supported."""
    if spec == "all":
        return [level for level in supported if level != "off"]
    if spec == "off":
        if "off" not in supported:
            raise CritError(f"{model}: level 'off' not supported (supported: {', '.join(supported)})")
        return ["off"]
    if ".." in spec:
        a, b = spec.split("..", 1)
        for level in (a, b):
            if level not in LEVEL_INDEX:
                raise CritError(f"{model}: unknown level {level!r} (LEVEL_ORDER: {', '.join(LEVEL_ORDER)})")
        lo, hi = LEVEL_INDEX[a], LEVEL_INDEX[b]
        wanted = list(LEVEL_ORDER[min(lo, hi) : max(lo, hi) + 1])
    else:
        wanted = [s.strip() for s in spec.split(",") if s.strip()]
    unsupported = [level for level in wanted if level not in supported]
    if unsupported:
        raise CritError(
            f"{model}: level(s) {', '.join(unsupported)} not supported (supported: {', '.join(supported)})"
        )
    return [level for level in wanted if level != "off" or spec == "off"]


def iso_from_ms(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_run_id(model, effort, started, harness_tag=""):
    """'<model>-<effort>-<YYYYMMDD-HHMMSS>' (`started` is the batch's start time), with '-<harness tag>'
    after the model for harnesses other than pi (e.g. 'claude-opus-5-5-cc-high-...'), so one model under
    two harnesses can't collide. URL/filesystem-safe: '@' becomes '-via-' (OpenRouter upstreams),
    anything else outside [a-z0-9.-] becomes '-'."""
    base, _, upstream = model.partition("@")  # the upstream may contain "/" itself ("deepinfra/fp8")
    model_short = base.rsplit("/", 1)[-1].lower() + (f"-via-{upstream.lower()}" if upstream else "")
    model_short = re.sub(r"[^a-z0-9.-]", "-", model_short) + (f"-{harness_tag}" if harness_tag else "")
    return f"{model_short}-{effort}-{started:%Y%m%d-%H%M%S}"


def title_from_slug(slug):
    return slug.replace("-", " ").capitalize()


def effort_sort_key(run):
    """Sort key for page.json: started_at, then effort order (LEVEL_ORDER, then alpha)."""
    return (run["started_at"], LEVEL_INDEX.get(run["effort"], 99), run["effort"])


def mask(secret):
    return secret[:4] + "…"
