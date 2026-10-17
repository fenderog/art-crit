// Shared wave function so the ocean mesh, the surfboard
// and the spray all agree on where the water surface is.

export function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.28 + t * 1.4) * 0.55 +
    Math.sin(z * 0.22 - t * 1.1) * 0.40 +
    Math.sin((x + z) * 0.13 + t * 0.7) * 0.25
  );
}

// Numerical slope helpers (used to tilt the surfboard).
export function waveSlopeX(x, z, t, d = 0.35) {
  return (waveHeight(x + d, z, t) - waveHeight(x - d, z, t)) / (2 * d);
}

export function waveSlopeZ(x, z, t, d = 0.35) {
  return (waveHeight(x, z + d, t) - waveHeight(x, z - d, t)) / (2 * d);
}
