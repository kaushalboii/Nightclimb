/**
 * A Fool's Errand - Hazard Manager
 * Handles rolling barrels and other traps
 */

import { CONFIG } from './config.js';
import { audioEngine } from './audio.js';
import { frameManager } from './frames.js';

export class HazardManager {
  constructor() {
    this.active = false;
    this.progress = 0;
    this.lane = 0;
    this.speed = CONFIG.BARREL.SPEED;
    this.animId = null;
    this.warningShown = false;
    this.collisionChecked = false;

    // DOM elements
    this.hazardLayer = null;
    this.barrelSprite = null;
    this.hazardAlert = null;
    this.gameStage = null;

    // Callbacks
    this.onCollision = null;
    this.onPassed = null;
    this.onWarningStart = null;
    this.onWarningEnd = null;
  }

  // Initialize DOM references
  initDOM(hazardLayer, barrelSprite, hazardAlert, gameStage) {
    this.hazardLayer = hazardLayer;
    this.barrelSprite = barrelSprite;
    this.hazardAlert = hazardAlert;
    this.gameStage = gameStage;
  }

  // Set collision callback
  setCallbacks({ onCollision, onPassed, onWarningStart, onWarningEnd }) {
    this.onCollision = onCollision;
    this.onPassed = onPassed;
    this.onWarningStart = onWarningStart;
    this.onWarningEnd = onWarningEnd;
  }

  // Check if barrel should spawn at current altitude
  shouldSpawn(altitude) {
    if (this.active) return false;
    if (altitude < CONFIG.BARREL.MIN_ALTITUDE_TO_SPAWN) return false;

    const chance = getBarrelSpawnChance(altitude);
    return Math.random() < chance;
  }

  // Trigger a new barrel hazard
  trigger() {
    if (this.active) return;

    this.active = true;
    this.progress = 0;
    this.warningShown = false;
    this.collisionChecked = false;

    // Random lane
    this.lane = CONFIG.BARREL.LANE_CHOICES[Math.floor(Math.random() * CONFIG.BARREL.LANE_CHOICES.length)];

    // Play warning sound
    audioEngine.playWarning();

    // Show warning banner
    this._showWarning();

    // Show barrel frame
    frameManager.showBarrelFrame();

    // Start animation after warning duration
    setTimeout(() => {
      this._startBarrelAnimation();
    }, CONFIG.BARREL.WARNING_DURATION_MS);
  }

  // Show warning banner
  _showWarning() {
    this.warningShown = true;
    if (this.hazardAlert) {
      this.hazardAlert.textContent = '⚠ BARREL ROLLING DOWN! DODGE [A/D]!';
      this.hazardAlert.classList.remove('hidden');
    }
    if (this.onWarningStart) this.onWarningStart();
  }

  // Hide warning banner
  _hideWarning() {
    if (this.hazardAlert) {
      this.hazardAlert.classList.add('hidden');
    }
    if (this.onWarningEnd) this.onWarningEnd();
  }

  // Start the barrel rolling animation
  _startBarrelAnimation() {
    this._hideWarning();

    if (this.hazardLayer) {
      this.hazardLayer.classList.remove('hidden');
    }

    frameManager.showBarrelActiveFrame();

    const stageHeight = this.gameStage ? this.gameStage.clientHeight : 500;
    const laneOffset = CONFIG.LANE_OFFSETS[this.lane] || 0;

    const animate = () => {
      if (!this.active) return;

      this.progress += this.speed;

      // Calculate barrel position
      const currentY = this.progress * (stageHeight + 100) - 50;
      const rotation = this.progress * 920; // Degrees

      if (this.barrelSprite) {
        this.barrelSprite.style.transform = `translate(calc(-50% + ${laneOffset}px), ${currentY}px) rotate(${rotation}deg)`;
      }

      // Collision check window
      if (!this.collisionChecked && this.progress >= CONFIG.BARREL.COLLISION_WINDOW_START && this.progress <= CONFIG.BARREL.COLLISION_WINDOW_END) {
        this.collisionChecked = true;
        if (this.onCollision) {
          this.onCollision(this.lane);
        }
      }

      // Barrel passed
      if (this.progress >= 1.0) {
        this._onBarrelPassed();
        return;
      }

      this.animId = requestAnimationFrame(animate);
    };

    this.animId = requestAnimationFrame(animate);
  }

  // Handle barrel passing without collision
  _onBarrelPassed() {
    this.active = false;
    this.progress = 0;
    this.collisionChecked = false;

    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }

    if (this.hazardLayer) {
      this.hazardLayer.classList.add('hidden');
    }

    if (this.hazardAlert) {
      this.hazardAlert.classList.add('hidden');
    }

    // Return to normal frame after a brief moment
    setTimeout(() => {
      frameManager.showAftermathFrame();
    }, 300);

    if (this.onPassed) this.onPassed();
  }

  // Handle collision with player
  handleCollision(playerLane) {
    if (!this.active) return false;

    const hit = playerLane === this.lane;

    if (hit) {
      this.active = false;

      if (this.animId) {
        cancelAnimationFrame(this.animId);
        this.animId = null;
      }

      if (this.hazardLayer) {
        this.hazardLayer.classList.add('hidden');
      }

      if (this.hazardAlert) {
        this.hazardAlert.classList.add('hidden');
      }

      // Play impact sound
      audioEngine.playImpact();

      // Screen shake via frame manager
      frameManager.shake();

      // Show death frame briefly
      frameManager.showDeathFrame();

      if (this.onCollision) {
        this.onCollision(this.lane, true); // true = hit
      }
    }

    return hit;
  }

  // Force stop any active barrel
  stop() {
    this.active = false;
    this.progress = 0;
    this.collisionChecked = false;

    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }

    if (this.hazardLayer) {
      this.hazardLayer.classList.add('hidden');
    }

    if (this.hazardAlert) {
      this.hazardAlert.classList.add('hidden');
    }
  }

  // Reset for new game
  reset() {
    this.stop();
    this.lane = 0;
    this.warningShown = false;
  }

  // Get current barrel lane (for debugging/UI)
  getCurrentLane() {
    return this.active ? this.lane : null;
  }

  // Get barrel progress (0-1)
  getProgress() {
    return this.progress;
  }

  isActive() {
    return this.active;
  }
}

// Helper function (also exported from config)
function getBarrelSpawnChance(altitude) {
  const stepsAboveMin = Math.max(0, altitude - CONFIG.BARREL.MIN_ALTITUDE_TO_SPAWN);
  const hundreds = stepsAboveMin / 100;
  const chance = CONFIG.BARREL.BASE_SPAWN_CHANCE + (hundreds * CONFIG.BARREL.CHANCE_INCREASE_PER_100_STEPS);
  return Math.min(chance, CONFIG.BARREL.MAX_SPAWN_CHANCE);
}

// Singleton instance
export const hazardManager = new HazardManager();