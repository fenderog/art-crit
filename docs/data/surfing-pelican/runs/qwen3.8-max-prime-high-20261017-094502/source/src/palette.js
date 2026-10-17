/**
 * Art direction: one palette + one sun for the whole scene, so the ocean,
 * sky, bird and board all read as the same late-afternoon moment.
 */
import * as THREE from "three";

export const PALETTE = {
  zenith:      "#1d5f96",
  midSky:      "#63a7c9",
  horizonSky:  "#f3c391",
  sunCore:     "#fff6df",
  sunGlow:     "#ffb765",

  deepWater:   "#04303f",
  midWater:    "#0a6a80",
  shallowWater:"#1fa8a3",
  crest:       "#8fe3dd",
  foam:        "#fdfaf3",
  haze:        "#e8b489",

  body:        "#f8f4ea",
  bodyShade:   "#ded3c2",
  wingTip:     "#33343c",
  beak:        "#f6bd45",
  beakTip:     "#e08a3c",
  pouch:       "#f2976b",
  leg:         "#f09a4d",
  eye:         "#1a1618",

  boardDeck:   "#f7efe1",
  boardBottom: "#e4553c",
  boardStripe: "#17a2a2",
  boardRail:   "#22303a",
  fin:         "#1c2a33",
};

export const C = Object.fromEntries(
  Object.entries(PALETTE).map(([k, v]) => [k, new THREE.Color(v)])
);

/** Low warm sun, off to the left and slightly behind the wave. */
export const SUN_DIR = new THREE.Vector3(-0.62, 0.235, -0.75).normalize();

export const SUN_COLOR = new THREE.Color("#ffd7a1");
export const SKY_LIGHT = new THREE.Color("#7fb6d8");
export const BOUNCE_LIGHT = new THREE.Color("#3fa8a0");

/** Direction the swell is mostly travelling in (used for board heading). */
export const SWELL_HEADING = new THREE.Vector3(1, 0, 0.18).normalize();
