/**
 * Procedural Web Audio API sound synthesizer for ocean surf, spray, and offshore wind.
 * 100% offline, generated completely in memory, 0 network requests.
 */

let audioCtx = null;
let isMuted = true;

// Audio nodes
let masterGain = null;
let oceanGain = null;
let oceanFilter = null;
let carveGain = null;
let carveFilter = null;
let windGain = null;

function createPinkNoiseBuffer(ctx, durationSec = 4) {
  const bufferSize = ctx.sampleRate * durationSec;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);

  let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
  for (let i = 0; i < bufferSize; i++) {
    const white = Math.random() * 2 - 1;
    b0 = 0.99886 * b0 + white * 0.0555179;
    b1 = 0.99332 * b1 + white * 0.0750759;
    b2 = 0.96900 * b2 + white * 0.1538520;
    b3 = 0.86650 * b3 + white * 0.3104856;
    b4 = 0.55000 * b4 + white * 0.5329522;
    b5 = -0.7616 * b5 - white * 0.0168980;
    data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
    b6 = white * 0.115926;
  }
  return buffer;
}

function createWhiteNoiseBuffer(ctx, durationSec = 2) {
  const bufferSize = ctx.sampleRate * durationSec;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }
  return buffer;
}

export function initAudio() {
  if (audioCtx) return;
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;

    audioCtx = new AudioContextClass();

    masterGain = audioCtx.createGain();
    masterGain.gain.setValueAtTime(0, audioCtx.currentTime);
    masterGain.connect(audioCtx.destination);

    // 1. Ocean surf rumble (looping pink noise through resonant lowpass)
    const pinkBuffer = createPinkNoiseBuffer(audioCtx, 5);
    const oceanSource = audioCtx.createBufferSource();
    oceanSource.buffer = pinkBuffer;
    oceanSource.loop = true;

    oceanFilter = audioCtx.createBiquadFilter();
    oceanFilter.type = 'lowpass';
    oceanFilter.frequency.setValueAtTime(450, audioCtx.currentTime);
    oceanFilter.Q.setValueAtTime(1.5, audioCtx.currentTime);

    oceanGain = audioCtx.createGain();
    oceanGain.gain.setValueAtTime(0.4, audioCtx.currentTime);

    oceanSource.connect(oceanFilter);
    oceanFilter.connect(oceanGain);
    oceanGain.connect(masterGain);
    oceanSource.start(0);

    // 2. Surfboard rail carve & spray hiss (white noise through bandpass)
    const whiteBuffer = createWhiteNoiseBuffer(audioCtx, 3);
    const carveSource = audioCtx.createBufferSource();
    carveSource.buffer = whiteBuffer;
    carveSource.loop = true;

    carveFilter = audioCtx.createBiquadFilter();
    carveFilter.type = 'bandpass';
    carveFilter.frequency.setValueAtTime(1600, audioCtx.currentTime);
    carveFilter.Q.setValueAtTime(2.0, audioCtx.currentTime);

    carveGain = audioCtx.createGain();
    carveGain.gain.setValueAtTime(0.05, audioCtx.currentTime);

    carveSource.connect(carveFilter);
    carveFilter.connect(carveGain);
    carveGain.connect(masterGain);
    carveSource.start(0);

    // 3. Gentle offshore wind hiss
    const windSource = audioCtx.createBufferSource();
    windSource.buffer = pinkBuffer;
    windSource.loop = true;

    const windFilter = audioCtx.createBiquadFilter();
    windFilter.type = 'bandpass';
    windFilter.frequency.setValueAtTime(800, audioCtx.currentTime);
    windFilter.Q.setValueAtTime(0.8, audioCtx.currentTime);

    windGain = audioCtx.createGain();
    windGain.gain.setValueAtTime(0.12, audioCtx.currentTime);

    windSource.connect(windFilter);
    windFilter.connect(windGain);
    windGain.connect(masterGain);
    windSource.start(0);

  } catch (err) {
    console.warn('Web Audio initialization error:', err);
  }
}

export function toggleAudio() {
  if (!audioCtx) {
    initAudio();
  }
  if (!audioCtx) return false;

  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }

  isMuted = !isMuted;
  if (masterGain) {
    const target = isMuted ? 0 : 0.8;
    masterGain.gain.setTargetAtTime(target, audioCtx.currentTime, 0.1);
  }
  return !isMuted;
}

export function getAudioState() {
  return !isMuted;
}

/**
 * Updates sound characteristics according to surfing physics
 * @param {number} carveIntensity 0 (straight trim) to 1 (hard rail turn / snap)
 * @param {boolean} inBarrel true if currently tucked in the barrel tube
 * @param {number} time current animation time
 */
export function updateAudio(carveIntensity, inBarrel, time) {
  if (!audioCtx || isMuted || !oceanGain) return;

  const now = audioCtx.currentTime;

  // Ocean swell rhythm: slow breathing wave cycles
  const waveCycle = Math.sin(time * 0.7) * 0.5 + 0.5;
  const oceanTargetFreq = inBarrel ? 280 : 380 + waveCycle * 250;
  oceanFilter.frequency.setTargetAtTime(oceanTargetFreq, now, 0.2);

  // Carving spray sound: sharp rushing water when turning
  const targetCarveGain = 0.04 + carveIntensity * 0.35 + (inBarrel ? 0.08 : 0);
  const targetCarveFreq = 1200 + carveIntensity * 1800;
  carveGain.gain.setTargetAtTime(targetCarveGain, now, 0.08);
  carveFilter.frequency.setTargetAtTime(targetCarveFreq, now, 0.08);
}
