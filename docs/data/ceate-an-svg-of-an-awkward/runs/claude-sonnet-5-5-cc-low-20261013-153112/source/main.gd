extends Control

func _ready() -> void:
	# Gentle "camera timer" zoom-in on the portrait.
	var p: Control = $Portrait
	p.pivot_offset = size / 2.0
	p.scale = Vector2(1.04, 1.04)
	create_tween().tween_property(p, "scale", Vector2.ONE, 2.0).set_trans(Tween.TRANS_SINE)
