# Rebuild the model and render the four reference-like views.
import bpy, time
ns = {}
exec(open("scripts/build_robie.py").read(), ns)
st = {}
exec(open("scripts/studio.py").read(), st)
st["setup_studio"]()
VIEWS = {
    "front": (4, 16, 3.9, (0, 0, 0.6)),
    "side_r": (-68, 24, 4.4, (-0.05, -0.05, 0.55)),
    "back": (180, 22, 4.6, (0, 0, 0.55)),
    "side_l": (102, 24, 4.4, (0.05, -0.05, 0.55)),
}
TAG = globals().get("TAG", "v")
RES = globals().get("RES", 560)
SAMPLES = globals().get("SAMPLES", 32)
ONLY = globals().get("ONLY", None)
t = time.time()
out = []
for k, (az, el, d, tgt) in VIEWS.items():
    if ONLY and k not in ONLY:
        continue
    st["set_camera"](az, el, d, target=tgt, lens=70)
    out.append(st["render"]("renders/%s_%s.png" % (TAG, k), res=(RES, RES), samples=SAMPLES))
result = {"files": out, "t": round(time.time() - t, 1)}
