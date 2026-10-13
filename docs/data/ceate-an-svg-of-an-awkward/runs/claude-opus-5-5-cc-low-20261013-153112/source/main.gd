extends Node2D
## Click or press Space to take the photo: a camera flash goes off.

@onready var flash: ColorRect = $Flash

func _unhandled_input(event: InputEvent) -> void:
	if (event is InputEventMouseButton and event.pressed) or event.is_action_pressed("ui_accept"):
		flash.modulate.a = 1.0
		create_tween().tween_property(flash, "modulate:a", 0.0, 0.6)
