extends Control

# Displays the portrait with a slow, awkward "hold the pose" camera drift.
@onready var portrait: TextureRect = $Portrait
var t := 0.0

func _process(delta: float) -> void:
	t += delta
	portrait.scale = Vector2.ONE * (1.01 + 0.008 * sin(t * 0.8))
	portrait.rotation = 0.004 * sin(t * 0.5)
