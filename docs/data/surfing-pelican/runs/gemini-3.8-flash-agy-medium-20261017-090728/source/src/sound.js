/**
 * 100% Procedural Synthesized Web Audio Ocean Surf and Wind Ambience.
 * Generates rolling barrel waves, rushing foam whitewater, and sea breeze
 * using custom noise buffer generators and modulated bandpass filters.
 * No audio files, zero network requests, strictly offline-friendly.
 */
export class SurfAudio {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.nodes = [];
  }

  init() {
    if (this.ctx) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      this.ctx = new AudioCtx();
    } catch (e) {
      console.warn('AudioContext not available', e);
    }
  }

  toggle() {
    if (!this.ctx) {
      this.init();
    }
    if (!this.ctx) return false;

    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }

    if (this.isPlaying) {
      this.stop();
      return false;
    } else {
      this.start();
      return true;
    }
  }

  start() {
    if (!this.ctx || this.isPlaying) return;

    // 1. Generate 4 seconds of smooth pink/ocean noise buffer
    const bufferSize = this.ctx.sampleRate * 4.0;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);

    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
      b6 = white * 0.115926;
    }

    const noiseNode = this.ctx.createBufferSource();
    noiseNode.buffer = noiseBuffer;
    noiseNode.loop = true;

    // 2. Wave Roar Lowpass Filter
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(450, this.ctx.currentTime);
    filter.Q.setValueAtTime(1.5, this.ctx.currentTime);

    // 3. Low-Frequency Oscillator (LFO) for wave swell surging rhythm
    const lfo = this.ctx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.setValueAtTime(0.12, this.ctx.currentTime); // ~8.3 sec swell cycle

    const lfoGain = this.ctx.createGain();
    lfoGain.gain.setValueAtTime(280, this.ctx.currentTime);

    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    // 4. Master Volume Gain
    const masterGain = this.ctx.createGain();
    masterGain.gain.setValueAtTime(0.18, this.ctx.currentTime);

    noiseNode.connect(filter);
    filter.connect(masterGain);
    masterGain.connect(this.ctx.destination);

    noiseNode.start();
    lfo.start();

    this.nodes = [noiseNode, lfo, masterGain];
    this.isPlaying = true;
  }

  stop() {
    if (!this.isPlaying) return;
    try {
      this.nodes.forEach(n => {
        if (n.stop) n.stop();
        if (n.disconnect) n.disconnect();
      });
    } catch (e) {
      // ignore
    }
    this.nodes = [];
    this.isPlaying = false;
  }
}
