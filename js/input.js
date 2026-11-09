/**
 * A Fool's Errand - Input Manager
 * Handles keyboard, mouse wheel, touch, virtual crank, and virtual buttons
 */

import { CONFIG } from './config.js';
import { audioEngine } from './audio.js';
import { playerManager } from './player.js';
import { hazardManager } from './hazards.js';
import { frameManager } from './frames.js';

export class InputManager {
  constructor() {
    // DOM Elements
    this.gameStage = null;
    this.crankContainer = null;
    this.crankArm = null;
    this.btnAscend = null;
    this.btnDodgeLeft = null;
    this.btnDodgeRight = null;
    this.startBtn = null;
    this.retryBtn = null;
    this.restartBtn = null;
    this.sfxToggleBtn = null;
    this.crtToggleBtn = null;
    this.flagHud = null; // For scroll modal (if implemented)

    // Input state
    this.keys = {};
    this.touchStartY = null;
    this.touchStartX = null;
    this.isCranking = false;
    this.lastCrankAngle = 0;
    this.crankAngle = 0;

    // Keyboard repeat
    this.keyRepeatTimers = {};
    this.keyRepeatDelays = {};

    // Callbacks
    this.onAscend = null;
    this.onDodge = null;
    this.onStartGame = null;
    this.onResume = null;
    this.onRestart = null;
    this.onToggleSFX = null;
    this.onToggleCRT = null;
  }

  // Initialize DOM references
  initDOM(elements) {
    this.gameStage = elements.gameStage;
    this.crankContainer = elements.crankContainer;
    this.crankArm = elements.crankArm;
    this.btnAscend = elements.btnAscend;
    this.btnDodgeLeft = elements.btnDodgeLeft;
    this.btnDodgeRight = elements.btnDodgeRight;
    this.startBtn = elements.startBtn;
    this.retryBtn = elements.retryBtn;
    this.restartBtn = elements.restartBtn;
    this.sfxToggleBtn = elements.sfxToggleBtn;
    this.crtToggleBtn = elements.crtToggleBtn;

    this._bindEvents();
  }

  // Bind all event listeners
  _bindEvents() {
    // Keyboard
    window.addEventListener('keydown', this._onKeyDown.bind(this));
    window.addEventListener('keyup', this._onKeyUp.bind(this));

    // Mouse wheel
    window.addEventListener('wheel', this._onWheel.bind(this), { passive: true });

    // Touch
    if (this.gameStage) {
      this.gameStage.addEventListener('touchstart', this._onTouchStart.bind(this), { passive: true });
      this.gameStage.addEventListener('touchmove', this._onTouchMove.bind(this), { passive: false });
      this.gameStage.addEventListener('touchend', this._onTouchEnd.bind(this), { passive: true });

      // Pointer for click-to-move
      this.gameStage.addEventListener('pointerdown', this._onPointerDown.bind(this));
    }

    // Virtual crank
    if (this.crankContainer) {
      this.crankContainer.addEventListener('mousedown', this._onCrankStart.bind(this));
      this.crankContainer.addEventListener('touchstart', this._onCrankStart.bind(this), { passive: false });
    }
    window.addEventListener('mousemove', this._onCrankMove.bind(this));
    window.addEventListener('touchmove', this._onCrankMove.bind(this), { passive: false });
    window.addEventListener('mouseup', this._onCrankEnd.bind(this));
    window.addEventListener('touchend', this._onCrankEnd.bind(this));

    // Virtual buttons
    if (this.btnAscend) {
      this.btnAscend.addEventListener('click', (e) => {
        e.stopPropagation();
        this._handleAscend();
      });
      this.btnAscend.addEventListener('touchstart', (e) => {
        e.stopPropagation();
        e.preventDefault();
        this._handleAscend();
      }, { passive: false });
    }

    if (this.btnDodgeLeft) {
      this.btnDodgeLeft.addEventListener('click', (e) => {
        e.stopPropagation();
        this._handleDodge(-1);
      });
      this.btnDodgeLeft.addEventListener('touchstart', (e) => {
        e.stopPropagation();
        e.preventDefault();
        this._handleDodge(-1);
      }, { passive: false });
    }

    if (this.btnDodgeRight) {
      this.btnDodgeRight.addEventListener('click', (e) => {
        e.stopPropagation();
        this._handleDodge(1);
      });
      this.btnDodgeRight.addEventListener('touchstart', (e) => {
        e.stopPropagation();
        e.preventDefault();
        this._handleDodge(1);
      }, { passive: false });
    }

    // Game control buttons
    if (this.startBtn) {
      this.startBtn.addEventListener('click', () => this._handleStartGame());
    }
    if (this.retryBtn) {
      this.retryBtn.addEventListener('click', () => this._handleResume());
    }
    if (this.restartBtn) {
      this.restartBtn.addEventListener('click', () => this._handleRestart());
    }

    // Settings toggles
    if (this.sfxToggleBtn) {
      this.sfxToggleBtn.addEventListener('click', () => this._handleToggleSFX());
    }
    if (this.crtToggleBtn) {
      this.crtToggleBtn.addEventListener('click', () => this._handleToggleCRT());
    }
  }

  // ========== KEYBOARD ==========
  _onKeyDown(e) {
    const key = e.key.toLowerCase();
    this.keys[key] = true;

    // Prevent default for game keys
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' ', 'w', 'a', 's', 'd'].includes(key)) {
      e.preventDefault();
    }

    // Handle immediate actions
    if (!playerManager.isGameStarted) {
      if (key === ' ' || key === 'enter') {
        this._handleStartGame();
      }
      return;
    }

    if (playerManager.isGameOver) {
      if (key === ' ' || key === 'enter') {
        this._handleResume();
      }
      return;
    }

    // Start key repeat for movement keys
    if (['arrowup', 'w', ' '].includes(key)) {
      this._startKeyRepeat('ascend', () => this._handleAscend());
    } else if (['arrowdown', 's'].includes(key)) {
      this._startKeyRepeat('descend', () => this._handleAscend(-1));
    } else if (['arrowleft', 'a'].includes(key)) {
      this._startKeyRepeat('dodgeLeft', () => this._handleDodge(-1));
    } else if (['arrowright', 'd'].includes(key)) {
      this._startKeyRepeat('dodgeRight', () => this._handleDodge(1));
    }
  }

  _onKeyUp(e) {
    const key = e.key.toLowerCase();
    this.keys[key] = false;

    // Stop key repeat
    if (['arrowup', 'w', ' '].includes(key)) {
      this._stopKeyRepeat('ascend');
      this._stopKeyRepeat('descend');
    } else if (['arrowdown', 's'].includes(key)) {
      this._stopKeyRepeat('descend');
    } else if (['arrowleft', 'a'].includes(key)) {
      this._stopKeyRepeat('dodgeLeft');
    } else if (['arrowright', 'd'].includes(key)) {
      this._stopKeyRepeat('dodgeRight');
    }
  }

  _startKeyRepeat(action, callback) {
    if (this.keyRepeatTimers[action]) return;

    // Initial fire
    callback();

    // Set up repeat
    this.keyRepeatDelays[action] = setTimeout(() => {
      this.keyRepeatTimers[action] = setInterval(callback, CONFIG.STEP.KEYBOARD_REPEAT_RATE);
    }, CONFIG.STEP.KEYBOARD_REPEAT_DELAY);
  }

  _stopKeyRepeat(action) {
    if (this.keyRepeatDelays[action]) {
      clearTimeout(this.keyRepeatDelays[action]);
      this.keyRepeatDelays[action] = null;
    }
    if (this.keyRepeatTimers[action]) {
      clearInterval(this.keyRepeatTimers[action]);
      this.keyRepeatTimers[action] = null;
    }
  }

  // ========== MOUSE WHEEL ==========
  _onWheel(e) {
    if (!playerManager.isGameStarted || playerManager.isGameOver) return;

    ensureAudio();

    // Scroll up = ascend, scroll down = also ascend (but slower) for continuous feel
    const delta = e.deltaY < 0 ? CONFIG.STEP.WHEEL_MULTIPLIER : CONFIG.STEP.WHEEL_MULTIPLIER * 0.5;
    this._handleAscend(delta);
  }

  // ========== TOUCH (Swipe) ==========
  _onTouchStart(e) {
    ensureAudio();

    // Ignore if touching UI elements
    if (e.target.closest('#crank-container') || e.target.closest('button')) return;

    if (e.touches.length > 0) {
      this.touchStartY = e.touches[0].clientY;
      this.touchStartX = e.touches[0].clientX;
    }
  }

  _onTouchMove(e) {
    if (!playerManager.isGameStarted || playerManager.isGameOver) return;
    if (this.touchStartY === null || e.touches.length === 0) return;

    const currentY = e.touches[0].clientY;
    const currentX = e.touches[0].clientX;
    const diffY = this.touchStartY - currentY; // Positive = upward swipe
    const diffX = currentX - this.touchStartX; // Positive = right swipe

    // Vertical ascend swipe
    if (diffY > CONFIG.STEP.SWIPE_THRESHOLD) {
      this._handleAscend(1);
      this.touchStartY = currentY; // Reset for continuous climbing
    }

    // Horizontal dodge swipes
    if (Math.abs(diffX) > CONFIG.STEP.SWIPE_HORIZONTAL_THRESHOLD) {
      if (diffX > 0) {
        this._handleDodge(1);
      } else {
        this._handleDodge(-1);
      }
      this.touchStartX = currentX; // Reset
    }
  }

  _onTouchEnd() {
    this.touchStartY = null;
    this.touchStartX = null;
  }

  // ========== POINTER (Click/Tap on Stage) ==========
  _onPointerDown(e) {
    if (!playerManager.isGameStarted || playerManager.isGameOver) return;

    ensureAudio();

    const rect = this.gameStage.getBoundingClientRect();
    const relativeX = (e.clientX - rect.left) / rect.width;

    if (relativeX < 0.33) {
      this._handleDodge(-1);
    } else if (relativeX > 0.66) {
      this._handleDodge(1);
    } else {
      this._handleAscend(1);
    }
  }

  // ========== VIRTUAL CRANK ==========
  _onCrankStart(e) {
    ensureAudio();
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    if (!clientX || !clientY) return;

    const rect = this.crankContainer.getBoundingClientRect();
    const cx = rect.left + rect.width * 0.5;
    const cy = rect.top + rect.height * 0.5;

    this.isCranking = true;
    this.lastCrankAngle = Math.atan2(clientY - cy, clientX - cx);

    // Prevent touch from also triggering stage swipe
    if (e.type === 'touchstart') {
      e.preventDefault();
      e.stopPropagation();
    }
  }

  _onCrankMove(e) {
    if (!this.isCranking) return;

    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    if (!clientX || !clientY) return;

    const rect = this.crankContainer.getBoundingClientRect();
    const cx = rect.left + rect.width * 0.5;
    const cy = rect.top + rect.height * 0.5;

    const newAngle = Math.atan2(clientY - cy, clientX - cx);
    let dAngle = newAngle - this.lastCrankAngle;

    // Normalize angle difference
    if (dAngle > Math.PI) dAngle -= Math.PI * 2;
    if (dAngle < -Math.PI) dAngle += Math.PI * 2;

    this.lastCrankAngle = newAngle;
    this.crankAngle += dAngle;

    // Update crank visual
    if (this.crankArm) {
      this.crankArm.style.transform = `translateY(-50%) rotate(${this.crankAngle}rad)`;
    }

    // Clockwise rotation = ascend
    const stepDelta = dAngle * 0.8;
    if (Math.abs(stepDelta) > 0.01) {
      this._handleAscend(stepDelta);
      audioEngine.playCrankClick();
    }

    if (e.type === 'touchmove') {
      e.preventDefault();
    }
  }

  _onCrankEnd() {
    this.isCranking = false;
  }

  // ========== ACTION HANDLERS ==========
  _handleAscend(delta = 1) {
    if (playerManager.ascend(delta)) {
      if (this.onAscend) this.onAscend(delta);
    }
  }

  _handleDodge(direction) {
    if (playerManager.dodge(direction)) {
      // Visual feedback
      const lane = playerManager.getLane();
      frameManager.applyLaneShift(lane);
      hudManager.showDodgeFeedback(lane);

      if (this.onDodge) this.onDodge(direction);
    }
  }

  _handleStartGame() {
    ensureAudio();
    playerManager.startGame();
    if (this.onStartGame) this.onStartGame();
  }

  _handleResume() {
    ensureAudio();
    playerManager.resumeFromCheckpoint();
    if (this.onResume) this.onResume();
  }

  _handleRestart() {
    ensureAudio();
    playerManager.restartFromBeginning();
    if (this.onRestart) this.onRestart();
  }

  _handleToggleSFX() {
    const enabled = playerManager.toggleSFX();
    hudManager.updateSFXStatus(enabled);
    if (this.onToggleSFX) this.onToggleSFX(enabled);
  }

  _handleToggleCRT() {
    const enabled = playerManager.toggleCRT();
    hudManager.toggleCRT(enabled);
    if (this.onToggleCRT) this.onToggleCRT(enabled);
  }

  // Update loop (called each frame)
  update(dt) {
    // Handle held keys for continuous movement
    if (playerManager.isGameStarted && !playerManager.isGameOver) {
      let keyDelta = 0;
      if (this.keys['arrowup'] || this.keys['w']) keyDelta += 8.0 * dt;
      if (this.keys['arrowdown'] || this.keys['s']) keyDelta -= 8.0 * dt;
      if (this.keys[' ']) keyDelta += 8.0 * dt; // Space also climbs

      if (keyDelta !== 0) {
        this._handleAscend(keyDelta);
      }
    }
  }
}

// Ensure audio context is ready
function ensureAudio() {
  audioEngine.ensureReady();
}

// Singleton instance
export const inputManager = new InputManager();