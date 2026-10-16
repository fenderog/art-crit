import sys, os, importlib
sys.path.insert(0, os.path.abspath('scripts'))
import lib, layout, octopus, arms, staging, booth, backdrop
mods = [lib, layout, octopus, arms, staging, booth, backdrop]
try:
    import props
    mods.append(props)
except ImportError:
    props = None
for m in mods:
    importlib.reload(m)
from lib import *
import layout as L

reset()
root = group("RamenBooth")
OM = octopus.octo_mats()
BM = booth.mats()

octo = group("Octopus_Chef", root)
octopus.build_body(octo, OM)
octopus.build_face(octo, OM)
octopus.build_toque(octo, OM)
octopus.build_scarf(octo, OM)
info = arms.build(octo, OM)

booth.build_all(root, BM)
if props is not None:
    props.build_all(root, BM, OM)

backdrop.build()
