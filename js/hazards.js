/**
 * A Fool's Errand - Hazard Manager
 * Handles rolling barrels and other traps using step-based physics
 */

import { CONFIG, getBarrelSpawnChance } from './config.js';
import { audioEngine } from './audio.js';
import { frameManager } from './frames.js';

export class HazardManager {
  constructor() {
    this.active = false;
    this.step = 0;           // Barrel's current step position
    this.lane = 0;           // Barrel's lane (-1, 0, 1)
    this.speed = 12.0;       // Steps per second
    this.rotation = 0;       // Visual rotation
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

  // Trigger a new barrel hazard at player's current step + offset
  trigger(playerStep) {
    if (this.active) return;

    this.active = true;
    this.step = playerStep + 16;  // Spawn ahead of player
    this.lane = CONFIG.BARREL.LANE_CHOICES[Math.floor(Math.random() * CONFIG.BARREL.LANE_CHOICES.length)];
    this.speed = 12.0 + Math.random() * 4.0;  // Variable speed
    this.rotation = 0;
    this.warningShown = false;
    this.collisionChecked = false;

    // Play warning sound
    audioEngine.playWarning();

    // Show warning banner
    this._showWarning();

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

  // Start the barrel rolling animation (step-based)
  _startBarrelAnimation() {
    this._hideWarning();

    if (this.hazardLayer) {
      this.hazardLayer.classList.remove('hidden');
    }

    frameManager.showBarrelActiveFrame();

    const animate = (dt) => {
      if (!this.active) return;

      // Move barrel down steps per second
      this.step -= this.speed * dt;
      this.rotation += this.speed * dt * 1.5;

      // Collision check near player elevation (within ~0.6 steps)
      // This will be checked by the game loop using player position

      // Barrel rolled past player (10 steps below)
      if (this.step < -10) {  // Will be compared to player step in game loop
        this._onBarrelPassed();
        return;
      }

      this.animId = requestAnimationFrame((time) => animate(time / 1000));
    };

    this.animId = requestAnimationFrame((time) => animate(time / 1000));
  }

  // Update barrel physics - called from game loop with player step
  update(playerStep, dt) {
    if (!this.active) return;

    // Move barrel down
    this.step -= this.speed * dt;
    this.rotation += this.speed * dt * 1.5;

    // Collision check window (when barrel is near player step)
    const stepDiff = this.step - playerStep;
    if (!this.collisionChecked && stepDiff >= -0.6 && stepDiff <= 0.6) {
      this.collisionChecked = true;
      if (this.onCollision) {
        this.onCollision(this.lane, false); // false = check only, not hit yet
      }
    }

    // Barrel passed player (well below)
    if (this.step < playerStep - 10) {
      this._onBarrelPassed();
    }
  }

  // Handle barrel passing without collision
  _onBarrelPassed() {
    this.active = false;
    this.step = 0;
    this.rotation = 0;
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

  // Handle collision with player - called when player dodges or gets hit
  checkCollision(playerLane) {
    if (!this.active) return false;

    const stepDiff = Math.abs(this.step - 0); // Player is at step 0 relative
    // Actually, collision is checked when barrel reaches player's position
    // The frame manager renders barrel at its step, player at step 0 (relative)

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
    this.step = 0;
    this.rotation = 0;
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

  // Get barrel step position
  getStep() {
    return this.step;
  }

  // Get barrel rotation
  getRotation() {
    return this.rotation;
  }

  // Get barrel speed
  getSpeed() {
    return this.speed;
  }

  // Get all barrel data for rendering
  _getBarrelData() {
    return {
      step: this.step,
      lane: this.lane,
      rotation: this.rotation,
      speed: this.speed,
      active: this.active
    };
  }

  // Get barrel progress (0-1) - legacy
  getProgress() {
    return this.active ? 1.0 : 0;
  }

  isActive() {
    return this.active;
  }
}

// Singleton instance
export const hazardManager = new HazardManager();