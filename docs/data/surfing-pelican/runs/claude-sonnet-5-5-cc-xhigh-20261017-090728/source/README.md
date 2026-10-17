# Surfing Pelican

A non-interactive, endlessly animated three.js scene: a white pelican on a coral surfboard
carving across the face of a glassy, curling wave, with the camera drifting between a long lens
out on the open water, a view from inside the pocket of the curl, and a 3/4 portrait.

Everything is generated in code. There are no image, model or font assets and no network access.

## Run

```sh
npm install
npx esbuild main.js --bundle --format=esm --outfile=dist/main.js   # then serve index.html + dist
```

`index.html` loads `main.js` as an ES module; `esbuild main.js --bundle --format=esm` is all the
packaging it needs.

## How it is put together

| file | what it does |
| --- | --- |
| `main.js` | renderer, lights, post stack (bloom, SMAA, grade), the loop, adaptive resolution |
| `src/profile.js` | cross-section of the breaking wave: three keyframes (shoulder, pitching lip, full barrel) |
| `src/wavefield.js` | how curl and size vary along the crest, shared by JS and GLSL |
| `src/water.js` | the sea: wave mesh displaced in the vertex shader, foam, translucency, wake, haze |
| `src/surface.js`, `src/surfer.js` | rides the exact surface the GPU draws; board orientation, lean, kinematics |
| `src/pelican.js` | procedural pelican: lofted body and neck, bill and gular pouch, feather-by-feather wings, IK legs |
| `src/board.js` | surfboard with painted deck and fins |
| `src/particles.js`, `src/spray.js`, `src/trail.js` | spray, mist, droplets and the foam wake |
| `src/rig.js` | the camera: three framings and the clearance rules that keep it out of the water |
| `src/sky.js`, `src/scenery.js` | procedural sky and image-based light, distant headland, gulls |
| `src/grade.js` | final colour grade and vignette |

## Notes

- The wave is a parametric profile (it can overhang, which a height field cannot), blended per slice
  along the crest and evaluated on the GPU. The same functions run in JS so the board sits on the water.
- The page picks its own render resolution to hold the frame rate.
- For development, `?t=12` renders one deterministic frame at 12 s, `?view=pelican` shows the bird alone,
  and `?cam=x,y,z,tx,ty,tz,fov` / `?rel=dx,dy,dz,fov` place the camera by hand.
