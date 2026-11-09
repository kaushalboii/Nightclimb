/**
 * A Fool's Errand - Player State Manager
 * Handles altitude, lanes, torches, checkpoints, and game state
 */

import { CONFIG } from './config.js';
import { audioEngine } from './audio.js';

export class PlayerManager {
  constructor() {
    // Core state
    this.altitude = CONFIG.STARTING_ALTITUDE;
    this.targetAltitude = CONFIG.STARTING_ALTITUDE;
    this.velocity = 0;
    this.isAlive = true;
    this.isGameStarted = false;
    this.isGameOver = false;

    // Lane system
    this.currentLane = CONFIG.LANES.MID;
    this.targetLane = CONFIG.LANES.MID;
    this.laneTransitionProgress = 1;

    // Torches (lives)
    this.torches = CONFIG.STARTING_TORCHES;

    // Checkpoints
    this.checkpointAltitude = CONFIG.STARTING_ALTITUDE;

    // Walking animation
    this.walkCycle = 0;
    this.lastFootstepAltitude = CONFIG.STARTING_ALTITUDE;

    // Cadence tracking
    this.stepCount = 0;
    this.lastCadenceTime = performance.now();
    this.currentCadence = 0;

    // High score
    this.highScore = 0;

    // Death info
    this.deathReason = '';
    this.deathTime = 0;

    // Settings
    this.settings = { ...CONFIG.DEFAULT_SETTINGS };

    // Callbacks
    this.onAltitudeChange = null;
    this.onLaneChange = null;
    this.onTorchChange = null;
    this.onCheckpointReached = null;
    this.onGameOver = null;
    this.onGameStart = null;
    this.onCadenceUpdate = null;
    this.onRankChange = null;
  }

  // Initialize from saved data
  loadFromStorage() {
    try {
      const savedCheckpoint = localStorage.getItem(CONFIG.STORAGE_KEYS.CHECKPOINT);
      const savedTorches = localStorage.getItem(CONFIG.STORAGE_KEYS.TORCHES);
      const savedHighScore = localStorage.getItem(CONFIG.STORAGE_KEYS.HIGH_SCORE);
      const savedSettings = localStorage.getItem(CONFIG.STORAGE_KEYS.SETTINGS);

      if (savedCheckpoint) {
        this.checkpointAltitude = parseInt(savedCheckpoint, 10);
      }
      if (savedTorches) {
        this.torches = parseInt(savedTorches, 10);
      }
      if (savedHighScore) {
        this.highScore = parseInt(savedHighScore, 10);
      }
      if (savedSettings) {
        this.settings = { ...CONFIG.DEFAULT_SETTINGS, ...JSON.parse(savedSettings) };
      }

      // Apply settings
      audioEngine.setEnabled(this.settings.sfxEnabled);
    } catch (e) {
      console.warn('Failed to load from storage:', e);
    }
  }

  // Save current state to storage
  saveToStorage() {
    try {
      localStorage.setItem(CONFIG.STORAGE_KEYS.CHECKPOINT, this.checkpointAltitude.toString());
      localStorage.setItem(CONFIG.STORAGE_KEYS.TORCHES, this.torches.toString());
      localStorage.setItem(CONFIG.STORAGE_KEYS.HIGH_SCORE, this.highScore.toString());
      localStorage.setItem(CONFIG.STORAGE_KEYS.SETTINGS, JSON.stringify(this.settings));
    } catch (e) {
      console.warn('Failed to save to storage:', e);
    }
  }

  // Start a new game
  startGame() {
    this.isGameStarted = true;
    this.isGameOver = false;
    this.isAlive = true;
    this.altitude = this.checkpointAltitude;
    this.targetAltitude = this.checkpointAltitude;
    this.currentLane = CONFIG.LANES.MID;
    this.targetLane = CONFIG.LANES.MID;
    this.torches = CONFIG.MAX_TORCHES;
    this.walkCycle = 0;
    this.lastFootstepAltitude = this.altitude;
    this.stepCount = 0;
    this.currentCadence = 0;
    this.deathReason = '';
    this.deathTime = 0;

    audioEngine.ensureReady();

    if (this.onGameStart) this.onGameStart();
    this._notifyAltitudeChange();
    this._notifyLaneChange();
    this._notifyTorchChange();
  }

  // Reset to checkpoint (after losing a torch)
  resumeFromCheckpoint() {
    this.isGameOver = false;
    this.isAlive = true;
    this.altitude = this.checkpointAltitude;
    this.targetAltitude = this.checkpointAltitude;
    this.currentLane = CONFIG.LANES.MID;
    this.targetLane = CONFIG.LANES.MID;
    this.walkCycle = 0;
    this.lastFootstepAltitude = this.altitude;
    this.deathReason = '';
    this.deathTime = 0;

    audioEngine.ensureReady();

    this._notifyAltitudeChange();
    this._notifyLaneChange();
  }

  // Full restart from bottom
  restartFromBeginning() {
    this.checkpointAltitude = CONFIG.STARTING_ALTITUDE;
    this.torches = CONFIG.STARTING_TORCHES;
    this.highScore = 0;
    this.saveToStorage();
    this.startGame();
  }

  // Game over
  gameOver(reason) {
    if (this.isGameOver) return;

    this.isGameOver = true;
    this.isAlive = false;
    this.deathReason = reason;
    this.deathTime = performance.now();

    // Update high score
    if (this.altitude > this.highScore) {
      this.highScore = this.altitude;
      this.saveToStorage();
    }

    audioEngine.playGameOver();

    if (this.onGameOver) this.onGameOver(reason);
  }

  // Ascend by steps
  ascend(steps = 1) {
    if (!this.isGameStarted || this.isGameOver || !this.isAlive) return false;

    const oldAltitude = this.altitude;
    this.targetAltitude += steps;

    // Update cadence
    this.stepCount += steps;
    const now = performance.now();
    if (now - this.lastCadenceTime >= 1000) {
      this.currentCadence = this.stepCount;
      this.stepCount = 0;
      this.lastCadenceTime = now;
      if (this.onCadenceUpdate) this.onCadenceUpdate(this.currentCadence);
    }

    // Play step sound and trigger walk cycle
    audioEngine.playStep();
    this._updateWalkCycle(steps);

    // Check for checkpoint
    this._checkCheckpoint();

    // Notify altitude change
    this._notifyAltitudeChange();

    return true;
  }

  // Dodge left or right
  dodge(direction) {
    if (!this.isGameStarted || this.isGameOver || !this.isAlive) return false;

    const newLane = Math.max(CONFIG.LANES.LEFT, Math.min(CONFIG.LANES.RIGHT, this.currentLane + direction));

    if (newLane !== this.currentLane) {
      this.currentLane = newLane;
      this.targetLane = newLane;

      audioEngine.playEvade();

      this._notifyLaneChange();
      return true;
    }
    return false;
  }

  // Update walk cycle animation
  _updateWalkCycle(steps) {
    const altitudeDiff = Math.abs(this.targetAltitude - this.lastFootstepAltitude);
    if (altitudeDiff >= 0.8) {
      this.lastFootstepAltitude = this.targetAltitude;
      this.walkCycle += 1;
    }
  }

  // Check if checkpoint reached
  _checkCheckpoint() {
    const nextCheckpoint = Math.floor(this.targetAltitude / CONFIG.CHECKPOINT_INTERVAL) * CONFIG.CHECKPOINT_INTERVAL;
    if (nextCheckpoint > this.checkpointAltitude && nextCheckpoint > 0) {
      this.checkpointAltitude = nextCheckpoint;
      this.torches = Math.min(this.torches + 1, CONFIG.MAX_TORCHES); // Bonus torch at checkpoint
      this.saveToStorage();
      audioEngine.playCheckpoint();
      if (this.onCheckpointReached) this.onCheckpointReached(this.checkpointAltitude);
      this._notifyTorchChange();
    }
  }

  // Lose a torch (hit by barrel)
  loseTorch() {
    this.torches = Math.max(0, this.torches - 1);
    this.saveToStorage();
    this._notifyTorchChange();

    if (this.torches <= 0) {
      this.gameOver('Crushed under the trap of rolled oak.');
    } else {
      // Knock back slightly
      this.targetAltitude = Math.max(this.checkpointAltitude, this.targetAltitude - 60);
      this._notifyAltitudeChange();
    }
  }

  // Update loop (called every frame)
  update(dt) {
    if (!this.isGameStarted || this.isGameOver) return;

    // Smooth altitude interpolation
    const diff = this.targetAltitude - this.altitude;
    this.velocity = diff * 12.0;
    this.altitude += this.velocity * dt;

    // Update walk cycle based on velocity
    if (Math.abs(this.velocity) > 0.05) {
      this.walkCycle += Math.abs(this.velocity) * dt * 4.5;
    }

    // Check rank change
    this._checkRankChange();
  }

  // Check for rank progression
  _checkRankChange() {
    const newRank = getRank(this.altitude);
    // Could notify rank change here if needed
  }

  // Toggle SFX
  toggleSFX() {
    this.settings.sfxEnabled = !this.settings.sfxEnabled;
    audioEngine.setEnabled(this.settings.sfxEnabled);
    this.saveToStorage();
    return this.settings.sfxEnabled;
  }

  // Toggle CRT
  toggleCRT() {
    this.settings.crtEnabled = !this.settings.crtEnabled;
    this.saveToStorage();
    return this.settings.crtEnabled;
  }

  // Toggle screen shake
  toggleScreenShake() {
    this.settings.screenShakeEnabled = !this.settings.screenShakeEnabled;
    this.saveToStorage();
    return this.settings.screenShakeEnabled;
  }

  // Getters
  getAltitude() { return Math.round(this.altitude); }
  getTargetAltitude() { return Math.round(this.targetAltitude); }
  getVelocity() { return this.velocity; }
  getLane() { return this.currentLane; }
  getLaneName() { return CONFIG.LANE_NAMES[this.currentLane]; }
  getTorches() { return this.torches; }
  getMaxTorches() { return CONFIG.MAX_TORCHES; }
  getCheckpoint() { return this.checkpointAltitude; }
  getHighScore() { return this.highScore; }
  getCadence() { return this.currentCadence; }
  getWalkCycle() { return this.walkCycle; }
  isMoving() { return Math.abs(this.velocity) > 0.05; }
  getSettings() { return { ...this.settings }; }

  // Notification methods
  _notifyAltitudeChange() {
    if (this.onAltitudeChange) this.onAltitudeChange(this.getAltitude());
  }

  _notifyLaneChange() {
    if (this.onLaneChange) this.onLaneChange(this.currentLane, this.getLaneName());
  }

  _notifyTorchChange() {
    if (this.onTorchChange) this.onTorchChange(this.torches, CONFIG.MAX_TORCHES);
  }

  // Set callbacks
  setCallbacks(callbacks) {
    Object.assign(this, callbacks);
  }
}

// Helper to get rank (also in config)
function getRank(currentStep) {
  let currentRank = CONFIG.RANKS[0];
  for (const rank of CONFIG.RANKS) {
    if (currentStep >= rank.minStep) {
      currentRank = rank;
    } else {
      break;
    }
  }
  return currentRank.title;
}

// Singleton instance
export const playerManager = new PlayerManager();