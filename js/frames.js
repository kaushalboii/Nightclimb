/**
 * A Fool's Errand - Frame Manager
 * Handles image loading, transitions, and animation cycling
 */

import { CONFIG } from './config.js';

export class FrameManager {
  constructor() {
    this.frames = CONFIG.FRAMES;
    this.currentIndex = 0;
    this.targetIndex = 0;
    this.transitioning = false;
    this.transitionProgress = 0;
    this.transitionStartTime = 0;
    this.loadedImages = new Map();
    this.stepCounter = 0;
    this.lastFrameStep = 0;

    // DOM elements
    this.stageImage = null;
    this.transitionOverlay = null;
    this.visualContainer = null;

    // Preload all frames
    this._preloadFrames();
  }

  // Initialize DOM references
  initDOM(stageImage, transitionOverlay, visualContainer) {
    this.stageImage = stageImage;
    this.transitionOverlay = transitionOverlay;
    this.visualContainer = visualContainer;

    // Set initial frame
    this.setFrame(CONFIG.FRAME_INDICES.DEFAULT, false);
  }

  // Preload all frame images
  async _preloadFrames() {
    const promises = this.frames.map((src, index) => {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          this.loadedImages.set(index, img);
          resolve();
        };
        img.onerror = () => {
          console.warn(`Failed to load frame ${index}: ${src}`);
          resolve();
        };
        img.src = src;
      });
    });

    await Promise.all(promises);
    console.log(`Preloaded ${this.loadedImages.size} frames`);
  }

  // Set frame with optional transition
  setFrame(index, animate = true) {
    if (!this.stageImage) return;

    const clampedIndex = ((index % this.frames.length) + this.frames.length) % this.frames.length;

    if (animate && this.currentIndex !== clampedIndex && this.transitionOverlay) {
      this._startTransition(clampedIndex);
    } else {
      this.currentIndex = clampedIndex;
      this._applyFrame(clampedIndex);
    }
  }

  // Start crossfade transition
  _startTransition(targetIndex) {
    this.targetIndex = targetIndex;
    this.transitioning = true;
    this.transitionProgress = 0;
    this.transitionStartTime = performance.now();

    // Show transition overlay
    this.transitionOverlay.classList.add('active');

    // After half transition, swap the actual image
    setTimeout(() => {
      this.currentIndex = this.targetIndex;
      this._applyFrame(this.targetIndex);
    }, CONFIG.FRAME_TRANSITION_MS / 2);

    // Complete transition
    setTimeout(() => {
      this.transitioning = false;
      this.transitionOverlay.classList.remove('active');
    }, CONFIG.FRAME_TRANSITION_MS);
  }

  // Apply frame to DOM
  _applyFrame(index) {
    const img = this.loadedImages.get(index);
    if (img && this.stageImage) {
      this.stageImage.src = this.frames[index];
    } else if (this.stageImage) {
      // Fallback to direct URL if not preloaded
      this.stageImage.src = this.frames[index];
    }
  }

  // Advance frame based on step count (cinematic cycling)
  advanceFrameIfNeeded(currentStep) {
    // Only advance every N steps for cinematic feel
    if (currentStep - this.lastFrameStep >= CONFIG.FRAME_CYCLE_INTERVAL) {
      this.lastFrameStep = currentStep;
      const nextIndex = (this.currentIndex + 1) % this.frames.length;
      this.setFrame(nextIndex, true);
    }
  }

  // Force specific frame for game events
  showBarrelFrame() {
    this.setFrame(CONFIG.FRAME_INDICES.BARREL_WARNING, true);
  }

  showBarrelActiveFrame() {
    this.setFrame(CONFIG.FRAME_INDICES.BARREL_ACTIVE, true);
  }

  showAftermathFrame() {
    this.setFrame(CONFIG.FRAME_INDICES.BARREL_AFTERMATH, true);
  }

  showDeathFrame() {
    this.setFrame(CONFIG.FRAME_INDICES.DEATH, true);
  }

  // Reset to default frame
  reset() {
    this.currentIndex = CONFIG.FRAME_INDICES.DEFAULT;
    this.targetIndex = CONFIG.FRAME_INDICES.DEFAULT;
    this.transitioning = false;
    this.stepCounter = 0;
    this.lastFrameStep = 0;
    this.setFrame(CONFIG.FRAME_INDICES.DEFAULT, false);
  }

  // Get current frame index
  getCurrentIndex() {
    return this.currentIndex;
  }

  // Apply vertical head-bob based on step
  applyVerticalBob(currentStep, isMoving) {
    if (!this.visualContainer) return;

    if (isMoving) {
      // Use step-based oscillation with controlled frequency
      const bobPhase = currentStep * CONFIG.VERTICAL_BOB_FREQUENCY;
      const bobY = Math.sin(bobPhase) * CONFIG.VERTICAL_BOB_AMPLITUDE;
      const scale = 1.02 + Math.cos(bobPhase) * 0.005;
      this.visualContainer.style.transform = `translateY(${bobY}px) scale(${scale})`;
    } else {
      // Smooth return to center
      this.visualContainer.style.transform = 'translateY(0px) scale(1.02)';
    }
  }

  // Apply lane shift (dodge visual feedback)
  applyLaneShift(lane, animate = true) {
    if (!this.visualContainer) return;

    const offsetX = CONFIG.LANE_OFFSETS[lane] || 0;

    if (animate) {
      this.visualContainer.style.transition = `transform ${CONFIG.EFFECTS.DODGE_RETURN_DURATION}ms ease-out`;
    } else {
      this.visualContainer.style.transition = 'none';
    }

    this.visualContainer.style.transform = `translateX(${offsetX}px)`;
  }

  // Return to center lane smoothly
  returnToCenter() {
    if (!this.visualContainer) return;

    this.visualContainer.style.transition = `transform ${CONFIG.EFFECTS.DODGE_RETURN_DURATION}ms ease-out`;
    this.visualContainer.style.transform = 'translateX(0px)';
  }

  // Screen shake effect
  shake(intensity = CONFIG.EFFECTS.SCREEN_SHAKE_INTENSITY, duration = CONFIG.EFFECTS.SCREEN_SHAKE_DURATION) {
    if (!this.visualContainer) return;

    const originalTransform = this.visualContainer.style.transform;
    let shakeCount = 0;
    const maxShakes = 6;
    const interval = duration / maxShakes;

    const doShake = () => {
      if (shakeCount >= maxShakes) {
        this.visualContainer.style.transform = originalTransform;
        return;
      }

      const offsetX = (Math.random() - 0.5) * intensity * 2;
      const offsetY = (Math.random() - 0.5) * intensity * 2;
      this.visualContainer.style.transform = `${originalTransform} translate(${offsetX}px, ${offsetY}px)`;

      shakeCount++;
      setTimeout(doShake, interval);
    };

    doShake();
  }
}

// Singleton instance
export const frameManager = new FrameManager();