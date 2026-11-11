/**
 * A Fool's Errand - Procedural Audio Engine
 * Web Audio API synthesis - zero external dependencies
 */

import { CONFIG } from './config.js';

export class AudioEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;
    this._initialized = false;
    this._userInteracted = false;
  }

  // Initialize audio context (must be called after user interaction)
  async init() {
    if (this._initialized) return;

    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();

      // Resume if suspended (browser autoplay policy)
      if (this.ctx.state === 'suspended') {
        await this.ctx.resume();
      }

      this._initialized = true;
    } catch (e) {
      console.warn('Audio context initialization failed:', e);
      this.enabled = false;
    }
  }

  // Call this on first user interaction
  async ensureReady() {
    if (!this._userInteracted) {
      this._userInteracted = true;
      await this.init();
    }
  }

  // Enable/disable all sounds
  setEnabled(enabled) {
    this.enabled = enabled;
  }

  isEnabled() {
    return this.enabled && this._initialized;
  }

  // Play stone step sound
  playStep() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(CONFIG.AUDIO.STEP_FREQ_START + Math.random() * 20, now);
    osc.frequency.exponentialRampToValueAtTime(CONFIG.AUDIO.STEP_FREQ_END, now + CONFIG.AUDIO.STEP_DURATION);

    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.005, now + CONFIG.AUDIO.STEP_DURATION);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + CONFIG.AUDIO.STEP_DURATION);

    // Gravel click layer
    this._playNoiseBurst(now, 0.015, 0.04, 0.06);
  }

  // Play dodge/evade sound
  playEvade() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(CONFIG.AUDIO.EVADE_FREQ_START, now);
    osc.frequency.exponentialRampToValueAtTime(CONFIG.AUDIO.EVADE_FREQ_END, now + CONFIG.AUDIO.EVADE_DURATION);

    gain.gain.setValueAtTime(0.18, now);
    gain.gain.exponentialRampToValueAtTime(0.005, now + CONFIG.AUDIO.EVADE_DURATION);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + CONFIG.AUDIO.EVADE_DURATION);
  }

  // Play barrel warning sound
  playWarning() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(CONFIG.AUDIO.WARNING_FREQ_START, now);
    osc.frequency.linearRampToValueAtTime(CONFIG.AUDIO.WARNING_FREQ_END, now + CONFIG.AUDIO.WARNING_DURATION);

    gain.gain.setValueAtTime(0.22, now);
    gain.gain.exponentialRampToValueAtTime(0.005, now + CONFIG.AUDIO.WARNING_DURATION);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + CONFIG.AUDIO.WARNING_DURATION);
  }

  // Play barrel impact/collision sound
  playImpact() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'square';
    osc.frequency.setValueAtTime(CONFIG.AUDIO.IMPACT_FREQ_START, now);
    osc.frequency.exponentialRampToValueAtTime(CONFIG.AUDIO.IMPACT_FREQ_END, now + CONFIG.AUDIO.IMPACT_DURATION);

    gain.gain.setValueAtTime(0.45, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + CONFIG.AUDIO.IMPACT_DURATION);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + CONFIG.AUDIO.IMPACT_DURATION);

    // Add noise burst for debris
    this._playNoiseBurst(now, 0.08, 0.15, 0.2);
  }

  // Play crank click (for virtual crank)
  playCrankClick() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(CONFIG.AUDIO.CRANK_CLICK_FREQ, now);
    osc.frequency.exponentialRampToValueAtTime(200, now + CONFIG.AUDIO.CRANK_CLICK_DURATION);

    gain.gain.setValueAtTime(0.06, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + CONFIG.AUDIO.CRANK_CLICK_DURATION);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + CONFIG.AUDIO.CRANK_CLICK_DURATION);
  }

  // Play checkpoint reached sound
  playCheckpoint() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    // Rising chime
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      const t = now + i * 0.08;
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.25);
    });
  }

  // Play game over sound
  playGameOver() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    // Descending minor chord
    [220, 174.61, 146.83, 110].forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.value = freq;
      const t = now + i * 0.15;
      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.5);
    });
  }

  // Play victory/level complete sound
  playVictory() {
    if (!this.isEnabled()) return;

    const now = this.ctx.currentTime;
    // Triumphant arpeggio
    [523.25, 659.25, 783.99, 1046.50, 1318.51].forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = freq;
      const t = now + i * 0.06;
      gain.gain.setValueAtTime(0.1, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.3);
    });
  }

  // Internal: Generate and play a noise burst
  _playNoiseBurst(startTime, gainValue, duration, decayTime) {
    const noiseBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * duration, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseBuffer.length; i++) {
      output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * decayTime));
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    const noiseGain = this.ctx.createGain();
    noiseGain.gain.setValueAtTime(gainValue, startTime);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
    whiteNoise.connect(noiseGain);
    noiseGain.connect(this.ctx.destination);
    whiteNoise.start(startTime);
  }
}

// Singleton instance
export const audioEngine = new AudioEngine();