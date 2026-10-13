extends Node2D
## Photo-studio toy: press Space / Enter / click to "take" the family portrait.
## A countdown of red lights blinks, the flash fires, and the picture jolts.

const CENTER := Vector2(600, 450)

@onready var portrait: Sprite2D = $Portrait

var _time := 0.0
var _countdown := -1 # lights remaining; -1 when idle
var _flash := 0.0
var _jolt := 0.0
var _shutter: AudioStreamPlayer
var _beep: AudioStreamPlayer


func _ready() -> void:
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	_shutter = _make_player(_make_shutter())
	_beep = _make_player(_make_beep())


func _unhandled_input(event: InputEvent) -> void:
	var pressed: bool = (event is InputEventMouseButton and event.pressed) \
		or (event is InputEventKey and event.pressed and not event.echo \
			and event.keycode in [KEY_SPACE, KEY_ENTER])
	if pressed and _countdown < 0:
		_take_photo()


func _take_photo() -> void:
	for i in range(3, 0, -1):
		_countdown = i
		_beep.play()
		queue_redraw()
		await get_tree().create_timer(0.6).timeout
	_countdown = -1
	_shutter.play()
	_flash = 1.0
	_jolt = 1.0


func _process(delta: float) -> void:
	_time += delta
	_flash = maxf(_flash - delta * 1.6, 0.0)
	_jolt = maxf(_jolt - delta * 2.5, 0.0)
	# Slow "studio" drift plus a startled jolt when the flash goes off.
	var drift := Vector2(sin(_time * 0.4) * 4.0, cos(_time * 0.3) * 3.0)
	var shake := Vector2(sin(_time * 70.0), cos(_time * 53.0)) * 6.0 * _jolt
	portrait.position = CENTER + drift + shake
	portrait.rotation = sin(_time * 0.5) * 0.004 + sin(_time * 40.0) * 0.01 * _jolt
	portrait.scale = Vector2.ONE * (1.0 + 0.02 * _jolt)
	queue_redraw()


func _draw() -> void:
	# Countdown lights on the camera (top centre of the frame).
	if _countdown > 0:
		for i in 3:
			var lit := i < _countdown
			var c := Color(1, 0.2, 0.15) if lit else Color(0.25, 0.08, 0.08)
			draw_circle(Vector2(560 + i * 40, 40), 11.0, Color(0, 0, 0, 0.6))
			draw_circle(Vector2(560 + i * 40, 40), 8.0, c)
	if _flash > 0.0:
		draw_rect(Rect2(Vector2(-200, -200), Vector2(1600, 1300)), Color(1, 1, 0.97, _flash))


func _make_player(stream: AudioStream) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.volume_db = -6.0
	add_child(p)
	return p


func _make_wav(samples: PackedFloat32Array, rate: int) -> AudioStreamWAV:
	var data := PackedByteArray()
	data.resize(samples.size() * 2)
	for i in samples.size():
		data.encode_s16(i * 2, int(clampf(samples[i], -1.0, 1.0) * 32000.0))
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = rate
	wav.data = data
	return wav


func _make_shutter() -> AudioStreamWAV:
	var rate := 22050
	var s := PackedFloat32Array()
	s.resize(int(rate * 0.18))
	for i in s.size():
		var t := float(i) / rate
		# Two clicks of filtered noise: the shutter opening and closing.
		var env := exp(-t * 90.0) + 0.7 * exp(-maxf(t - 0.07, 0.0) * 120.0) * float(t > 0.07)
		s[i] = randf_range(-1.0, 1.0) * env * 0.8
	return _make_wav(s, rate)


func _make_beep() -> AudioStreamWAV:
	var rate := 22050
	var s := PackedFloat32Array()
	s.resize(int(rate * 0.09))
	for i in s.size():
		var t := float(i) / rate
		s[i] = sin(TAU * 1320.0 * t) * 0.35 * minf(1.0, (0.09 - t) * 60.0)
	return _make_wav(s, rate)
