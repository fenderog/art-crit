extends Node2D

var captured := false
var shots := 0
var shutter := 0.0
var hover := false
var motion := Vector2.ZERO
var player: AudioStreamPlayer

func _ready() -> void:
	# A tiny synthesized shutter keeps the project entirely asset-independent.
	var sound := AudioStreamWAV.new()
	sound.format = AudioStreamWAV.FORMAT_16_BITS
	sound.mix_rate = 22050
	var bytes := PackedByteArray()
	bytes.resize(4400)
	var rng := RandomNumberGenerator.new()
	rng.seed = 18
	for i in range(2200):
		var envelope := exp(-float(i) / 330.0)
		var sample := int(rng.randf_range(-1.0, 1.0) * envelope * 16000.0)
		bytes.encode_s16(i * 2, sample)
	sound.data = bytes
	player = AudioStreamPlayer.new()
	player.stream = sound
	player.volume_db = -12
	add_child(player)

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		take_photo()
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE or event.keycode == KEY_ENTER:
			take_photo()
		elif event.keycode == KEY_R or event.keycode == KEY_ESCAPE:
			captured = false
			queue_redraw()

func take_photo() -> void:
	if captured:
		captured = false
	else:
		captured = true
		shots = mini(shots + 1, 8)
		shutter = 1.0
		player.play()
	queue_redraw()

func _process(delta: float) -> void:
	var mouse := get_global_mouse_position()
	hover = mouse.distance_to(Vector2(1080, 853)) < 29
	var target := Vector2.ZERO if captured else (mouse - Vector2(600, 450)).clamp(Vector2(-600, -450), Vector2(600, 450)) / 180.0
	motion = motion.lerp(target, 1.0 - exp(-delta * 3.0))
	if not captured:
		$Portrait.position = Vector2(600, 450) + motion
		$Portrait.rotation = motion.x * 0.001
	shutter = maxf(0, shutter - delta * 2.8)
	$Flash/White.color.a = shutter * shutter * 0.85
	queue_redraw()

func _draw() -> void:
	var ink := Color("354d52")
	var center := Vector2(1080, 853)
	draw_circle(center, 27, Color("d8c8a5") if hover else Color("e5dbc4"))
	draw_arc(center, 27, 0, TAU, 64, ink, 1.5, true)
	if captured:
		# A rewind glyph invites another attempt at a less awkward photograph.
		draw_arc(center, 11, -1.1, 4.3, 32, ink, 2.0, true)
		draw_polyline(PackedVector2Array([center + Vector2(-11, -13), center + Vector2(-6, -8), center + Vector2(0, -14)]), ink, 2, true)
	else:
		draw_style_box(camera_box(), Rect2(center - Vector2(16, 10), Vector2(32, 23)))
		draw_rect(Rect2(center - Vector2(9, 15), Vector2(13, 5)), ink)
		draw_arc(center + Vector2(0, 1), 7, 0, TAU, 32, ink, 2, true)
	for i in range(shots):
		draw_circle(Vector2(100 + i * 13, 857), 2.5, Color("a58b62"))

func camera_box() -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = Color(0, 0, 0, 0)
	box.border_color = Color("354d52")
	box.set_border_width_all(2)
	box.set_corner_radius_all(3)
	return box
