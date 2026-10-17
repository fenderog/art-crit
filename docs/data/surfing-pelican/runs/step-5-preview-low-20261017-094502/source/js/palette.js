// Shared colour palette for the whole scene.
// Colours are authored as sRGB hex strings; three.js converts them to the
// linear working space for us (ColorManagement is enabled by default).

export const PALETTE = {
  // sun / sky
  sun: '#ffd8a0',
  skyTop: '#12508f',
  skyMid: '#6aa9d4',
  skyHorizon: '#f8d6a6',
  haze: '#f0cba4',
  cloud: '#ffffff',
  cloudShade: '#b9a794',

  // ocean
  deep: '#0e4257',
  shallow: '#1e879b',
  sss: '#7fe3d0',
  foam: '#fdfdfd',

  // landscape
  island: '#2c5a52',
  gull: '#39465a',

  // pelican
  body: '#f8f5ee',
  wing: '#ece7dc',
  wingTip: '#5b6779',
  beak: '#f0a63c',
  pouch: '#e3813a',
  foot: '#e79a3c',
  bandana: '#d9484c',
  eye: '#20242c',

  // board
  deck: '#f7efdd',
  stringer: '#d9484c',
  pinstripe: '#e8c46a',
  fin: '#d9484c',
};

// Sun direction (points *from* the scene *towards* the sun).
export const SUN_DIR = { x: 0.44, y: 0.2, z: 0.87 };

export const FOG_DENSITY = 0.00068;
