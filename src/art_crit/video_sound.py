"""The sound of `art-crit video`: a quiet four-on-the-floor beat plus a whoosh on every cut, pops when things land and
ticks while text types or numbers count, synthesized here with the standard library into a WAV (no samples, nothing
licensed). `video.cues` says when each sound plays; ADR-0033."""

import math
import random
import wave
from array import array
from functools import cache

RATE = 44100
BEAT_S = 0.5  # 120 bpm; the timeline's cuts fall on beats
GAIN = {"kick": 0.5, "hat": 0.09, "whoosh": 0.42, "pop": 0.3, "tick": 0.1, "hit": 0.75, "ding": 0.3}


def _env(n, decay):
    return [math.exp(-decay * k / RATE) for k in range(n)]


def _sweep(n, f0, f1, rate):
    """A sine whose pitch glides from f0 to f1 (exponentially, at `rate` per second)."""
    out, phase = [], 0.0
    for k in range(n):
        f = f1 + (f0 - f1) * math.exp(-rate * k / RATE)
        phase += 2 * math.pi * f / RATE
        out.append(math.sin(phase))
    return out


def _noise(n, seed):
    rng = random.Random(seed)
    return [rng.uniform(-1, 1) for _ in range(n)]


@cache
def sound(kind):
    """One sound as a tuple of samples in -1..1."""
    if kind == "kick":
        n = int(0.3 * RATE)
        return tuple(s * e for s, e in zip(_sweep(n, 150, 46, 32), _env(n, 11)))
    if kind == "hat":
        n = int(0.05 * RATE)
        x = _noise(n + 1, 1)
        return tuple((x[k + 1] - x[k]) * 0.5 * e for k, e in enumerate(_env(n, 95)))
    if kind == "whoosh":  # noise through a low-pass whose cutoff rises and falls
        n = int(0.42 * RATE)
        y, out = 0.0, []
        for k, x in enumerate(_noise(n, 2)):
            u = k / n
            cutoff = 250 + 5200 * math.sin(math.pi * u) ** 2
            y += (1 - math.exp(-2 * math.pi * cutoff / RATE)) * (x - y)
            out.append(y * math.sin(math.pi * u) ** 1.5 * 2.2)
        return tuple(out)
    if kind == "pop":
        n = int(0.11 * RATE)
        return tuple(s * e for s, e in zip(_sweep(n, 320, 980, 60), _env(n, 38)))
    if kind == "tick":
        n = int(0.018 * RATE)
        return tuple(math.sin(2 * math.pi * 2600 * k / RATE) * e for k, e in enumerate(_env(n, 260)))
    if kind == "hit":  # a big kick under a burst of low noise
        n = int(0.5 * RATE)
        low, y = [], 0.0
        for x in _noise(n, 3):
            y += 0.06 * (x - y)
            low.append(y * 3)
        return tuple((k + l) * e for k, l, e in zip(_sweep(n, 180, 40, 18), low, _env(n, 7)))
    if kind == "ding":
        n = int(1.1 * RATE)
        return tuple((math.sin(2 * math.pi * 1318.5 * k / RATE) + 0.6 * math.sin(2 * math.pi * 1975.5 * k / RATE)) / 1.6 * e
                     for k, e in enumerate(_env(n, 4.5)))
    raise ValueError(f"unknown sound {kind!r}")


def soundtrack(cues, seconds, path):
    """Write `seconds` of mono 16-bit sound to `path`: the beat, plus each (time in s, kind) cue."""
    n = round(seconds * RATE)
    mix = array("d", bytes(8 * n))
    beats = [(k * BEAT_S, "kick") for k in range(int(seconds / BEAT_S))]
    beats += [(k * BEAT_S + BEAT_S / 2, "hat") for k in range(int(seconds / BEAT_S))]
    for at, kind in [*beats, *cues]:
        start, gain = round(at * RATE), GAIN[kind]
        for k, s in enumerate(sound(kind)[:max(0, n - start)], start):
            if k >= 0:
                mix[k] += s * gain
    fade = int(0.25 * RATE)  # the end fades so a looping video doesn't click
    for k in range(max(0, n - fade), n):
        mix[k] *= (n - k) / fade
    pcm = array("h", (int(32000 * math.tanh(x)) for x in mix))  # a soft limiter: never clips
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
