# Final build: renders to ./output and a GLB export of the toy at real-world scale.
import bpy, os, time
ns = {}
exec(open("scripts/build_robie.py").read(), ns)
st = {}
exec(open("scripts/studio.py").read(), st)
st["setup_studio"]()

OUT = os.path.abspath("output")
os.makedirs(OUT, exist_ok=True)
SAMPLES = globals().get("SAMPLES", 256)
RES = globals().get("RES", 1600)
DO_RENDERS = globals().get("DO_RENDERS", True)

SHOTS = [
    ("robie_hero_three_quarter", (-32, 17, 4.5, (0.0, -0.1, 0.54))),
    ("robie_front", (0, 13, 4.3, (0.0, -0.1, 0.6))),
    ("robie_right_profile", (-90, 9, 4.3, (0.0, -0.1, 0.6))),
    ("robie_rear_lid", (148, 33, 4.5, (0.2, -0.08, 0.58))),
]
t = time.time()
files = []
if DO_RENDERS:
    for name, (az, el, d, tgt) in SHOTS:
        st["set_camera"](az, el, d, target=tgt, lens=70)
        files.append(st["render"](os.path.join(OUT, name + ".jpg"), res=(RES, RES),
                                  samples=SAMPLES, fmt='JPEG', quality=90))

# ---- GLB export: parent the toy under one root at real-world scale ----
robot = bpy.data.collections["Robie"]
root = bpy.data.objects.new("Robie_RoboticBanker", None)
robot.objects.link(root)
for o in list(robot.objects):
    if o is not root and o.parent is None:
        o.parent = root
root.scale = (0.13, 0.13, 0.13)          # body diameter ~13 cm
bpy.context.view_layer.update()
for o in bpy.context.view_layer.objects:
    o.select_set(o.name in robot.all_objects)
bpy.context.view_layer.objects.active = root
glb = os.path.join(OUT, "robie_robotic_banker.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                          export_apply=True, export_cameras=False, export_lights=False,
                          export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("robie.blend"))
result = {"files": files, "glb": glb, "glb_bytes": os.path.getsize(glb), "t": round(time.time() - t, 1)}
