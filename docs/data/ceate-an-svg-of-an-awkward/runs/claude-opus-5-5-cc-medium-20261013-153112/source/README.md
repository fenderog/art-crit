# Awkward Robot Family Portrait

A framed SVG portrait (`portrait.svg`) of a robot family in an awkward photo-studio sitting, shown in a small Godot 4.7 scene:

- **Dad** is tall and stiff. He grins way too hard, sweats coolant, and holds his hand *just* above Mom's shoulder.
- **Mom** holds a pose with a polite smile while side-eyeing the hovering hand and cradling the wailing, sparking **baby**.
- **Grandpa** is rusty and asleep in the wingback chair. He's wearing fuzzy slippers and drooling oil.
- **Little sibling** stands on a crate, waves at the camera and stretches a telescoping arm behind Dad's head to give him bunny ears.
- **The teen** wears headphones, folds their arms and leans away from everyone at the far edge.
- **Robo-dog** is staring at a mechanical butterfly instead of the camera.

## Run

1. Open this folder in Godot 4.7 (`godot --path .`) or import `project.godot` from the Project Manager.
2. Press **F5** (main scene: `main.tscn`).

## Controls

- **Space / Enter / click**: take the photo. A 3-light countdown runs, then the flash and shutter fire.

It uses the GL Compatibility renderer with no threads, so it's suitable for a web export. All sound is generated in code, so there are no external assets.
