// The interactive 3D view of a model-made .glb (blender kind): orbit (drag), zoom (wheel/pinch) and pan (right-drag).
// A .glb is data, not code: three.js parses it here, nothing in it runs. The vendored three.js bundle (~640 KB) is only
// fetched the first time a model is opened, so pages without models never load it.

let three = null;
const loadThree = () => (three ??= import("./vendor/three-gltf.min.js"));

// Loads `url` into `host` (an empty element that has a size) and keeps it rendered until the host leaves the page.
// Renders on demand (after a camera move or a resize) unless the model has animations, which play in a loop.
export async function mountModel(host, url) {
  const T = await loadThree();
  const renderer = new T.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  host.append(renderer.domElement);

  const scene = new T.Scene();
  const pmrem = new T.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new T.RoomEnvironment(), 0.04).texture; // soft studio light for unlit exports
  const camera = new T.PerspectiveCamera(40, 1, 0.01, 1000);
  const controls = new T.OrbitControls(camera, renderer.domElement);

  const gltf = await new T.GLTFLoader().loadAsync(url);
  if (!gltf.scene) throw new Error("the .glb has no scene");
  scene.add(gltf.scene);
  frame(T, gltf.scene, camera, controls);

  const mixer = gltf.animations.length ? new T.AnimationMixer(gltf.scene) : null;
  for (const clip of gltf.animations) mixer.clipAction(clip).play();
  const timer = new T.Timer();
  const render = () => renderer.render(scene, camera);
  const resize = () => {
    const { clientWidth: w, clientHeight: h } = host;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    render();
  };
  const observer = new ResizeObserver(resize);
  observer.observe(host);
  controls.addEventListener("change", render);
  resize();
  host.dataset.loaded = "true"; // the model is in the scene (tests wait for this)

  const tick = () => {
    if (!host.isConnected) { // the card was redrawn (filters, sorting): free the WebGL context
      observer.disconnect();
      controls.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      return;
    }
    if (mixer) {
      timer.update();
      mixer.update(timer.getDelta());
      render();
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

// Points the camera at the model from the front, a little above, far enough to see all of it.
function frame(T, object, camera, controls) {
  const box = new T.Box3().setFromObject(object);
  if (box.isEmpty()) return;
  const size = box.getSize(new T.Vector3()).length() || 1;
  const center = box.getCenter(new T.Vector3());
  const distance = size / (2 * Math.tan((camera.fov * Math.PI) / 360));
  camera.near = size / 100;
  camera.far = size * 100;
  camera.position.copy(center).add(new T.Vector3(0.6, 0.45, 1).normalize().multiplyScalar(distance));
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}
