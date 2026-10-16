import sys
D = "<vol>/dev/art-crit-runs/2026-10-16-092538-3d-octopus-ramen-shop/claude-sonnet-5-5-cc-high-20261016-092538/work/build/"
NS = globals()
exec(open(D + "helpers.py").read(), NS)
clear()
for f in ("booth.py", "octopus.py", "finish.py"):
    exec(open(D + f).read(), NS)
result = {"objects": len(bpy.data.objects)}
