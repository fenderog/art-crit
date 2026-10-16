// Flint — design parameters and palette (single source of truth for every output).

export const palette = {
  chalk: '#F4F0EA',   // paper / background
  oat: '#DDD3C5',
  sand: '#C2B4A1',
  stone: '#A39888',
  taupe: '#857566',
  basalt: '#332F2B',  // ink
  night: '#262320',   // reversed background
};

// Mark: a river stone split by four fissures around a negative-space spark.
export const markParams = {
  stone: { r: 97, harm: [[2, 0.06, 0.3], [3, 0.025, 1.6]], squash: 0.93 },
  spark: { tips: [62, 46, 62, 46], c: 0.62, rot: -8, centre: [0, 0] },
  fissure: { bend: 24, reach: 90, w: 3.6 },
  edgeRound: 7,
  box: [-112, -108, 112, 108],
  step: 0.2, fitErr: 0.03, spacing: 0.35,
};

// Fragment tones, clockwise from top-left: lit from the upper left, settling into shadow.
export const fragmentTones = {
  light: ['oat', 'sand', 'basalt', 'taupe'],
  dark: ['oat', 'sand', 'stone', 'taupe'],
};

// Wordmark: x-height 100 units.
export const wordParams = {
  X: 100, A: 142, T: 124, W: 19, soft: 2.4, crotch: 3, over: 1.5,
  fHook: 24, fSweep: 95, barL: 22, barR: 28, barW: 0.9, tFoot: 22, tSweep: 100,
  dFL: 55, dLI: 48, dIN: 48, dNT: 51, nR: 37.5,
  dotR: 10.5, dotGap: 15, dotDx: 0, dotTilt: -25, dotAspect: 1.08,
  step: 0.12,
};
