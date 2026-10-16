# Camera shots used for previews and final renders.
SHOTS = {
    "hero":  dict(loc=(-1.8, -3.95, 1.38), target=(0.0, 0.3, 1.70), lens=30, fstop=4.0, focus=(0.0, 0.5, 1.5)),
    "close": dict(loc=(-0.75, -1.9, 1.42), target=(0.0, 0.3, 1.38), lens=32, fstop=5.6, focus=(0.0, 0.45, 1.45)),
    "high":  dict(loc=(1.25, -2.1, 2.25), target=(-0.05, 0.15, 1.2), lens=28, fstop=None, focus=None),
    "back":  dict(loc=(-1.0, 3.55, 1.9), target=(0.05, 0.6, 1.15), lens=28, fstop=5.6, focus=(0.0, 0.9, 1.1)),
}


def render_shot(name, path, res=(960, 640), samples=48, jpeg=None):
    sh = SHOTS[name]
    cam = make_camera("Cam_" + name, sh["loc"], sh["target"], lens=sh["lens"], fstop=sh["fstop"], focus=sh["focus"])
    bpy.context.scene.camera = cam
    setup_render('CYCLES', samples, res)
    bpy.context.scene.render.filepath = os.path.abspath(path)
    st = bpy.context.scene.render.image_settings
    if jpeg:
        st.file_format = 'JPEG'
        st.quality = jpeg
    else:
        st.file_format = 'PNG'
    if samples > 64:
        bpy.context.scene.cycles.adaptive_threshold = 0.015
    bpy.ops.render.render(write_still=True)
