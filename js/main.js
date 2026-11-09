/**
 * A Fool's Errand - Main Entry Point
 * Initializes all systems and runs the game loop
 */

import { CONFIG } from './config.js';
import { audioEngine } from './audio.js';
import { frameManager } from './frames.js';
import { hazardManager } from './hazards.js';
import { playerManager } from './player.js';
import { hudManager } from './hud.js';
import { inputManager } from './input.js';

// Game state
let lastTime = performance.now();
let animationId = null;

// DOM Elements cache
const elements = {};

/**
 * Initialize all DOM references
 */
function cacheDOMElements() {
  elements.stageImage = document.getElementById('stage-image');
  elements.transitionOverlay = document.getElementById('frame-transition');
  elements.visualContainer = document.getElementById('visual-frame-container');
  elements.hazardLayer = document.getElementById('hazard-layer');
  elements.barrelSprite = document.getElementById('barrel-sprite');
  elements.hazardAlert = document.getElementById('hazard-alert');
  elements.gameStage = document.getElementById('game-stage');
  elements.crankContainer = document.getElementById('crank-container');
  elements.crankArm = document.getElementById('crank-arm');
  elements.btnAscend = document.getElementById('btn-ascend-step');
  elements.btnDodgeLeft = document.getElementById('btn-dodge-left');
  elements.btnDodgeRight = document.getElementById('btn-dodge-right');
  elements.startBtn = document.getElementById('start-game-btn');
  elements.retryBtn = document.getElementById('retry-btn');
  elements.restartBtn = document.getElementById('restart-all-btn');
  elements.sfxToggleBtn = document.getElementById('sfx-toggle-btn');
  elements.crtToggleBtn = document.getElementById('crt-toggle-btn');
  elements.sfxStatus = document.getElementById('sfx-status');
  elements.scanlineOverlay = document.getElementById('scanline-overlay');
  elements.altitudeDisplay = document.getElementById('altitude-display');
  elements.laneIndicator = document.getElementById('lane-indicator');
  elements.actIndicator = document.getElementById('act-indicator');
  elements.poemText = document.getElementById('poem-text');
  elements.torchesCount = document.getElementById('torches-count');
  elements.speedMeter = document.getElementById('speed-meter');
  elements.rankTitle = document.getElementById('rank-title');
  elements.titleOverlay = document.getElementById('title-overlay');
  elements.gameOverOverlay = document.getElementById('game-over-overlay');
  elements.gameOverReason = document.getElementById('game-over-reason');
  elements.dodgeTag = document.getElementById('dodge-tag');
}

/**
 * Initialize all managers with DOM references
 */
function initializeManagers() {
  // Frame manager
  frameManager.initDOM(
    elements.stageImage,
    elements.transitionOverlay,
    elements.visualContainer
  );

  // Hazard manager
  hazardManager.initDOM(
    elements.hazardLayer,
    elements.barrelSprite,
    elements.hazardAlert,
    elements.gameStage
  );

  // HUD manager
  hudManager.initDOM({
    altitudeDisplay: elements.altitudeDisplay,
    laneIndicator: elements.laneIndicator,
    actIndicator: elements.actIndicator,
    poemText: elements.poemText,
    torchesCount: elements.torchesCount,
    speedMeter: elements.speedMeter,
    rankTitle: elements.rankTitle,
    titleOverlay: elements.titleOverlay,
    gameOverOverlay: elements.gameOverOverlay,
    gameOverReason: elements.gameOverReason,
    dodgeTag: elements.dodgeTag,
    sfxStatus: elements.sfxStatus,
    scanlineOverlay: elements.scanlineOverlay,
    crtToggleBtn: elements.crtToggleBtn
  });

  // Input manager
  inputManager.initDOM({
    gameStage: elements.gameStage,
    crankContainer: elements.crankContainer,
    crankArm: elements.crankArm,
    btnAscend: elements.btnAscend,
    btnDodgeLeft: elements.btnDodgeLeft,
    btnDodgeRight: elements.btnDodgeRight,
    startBtn: elements.startBtn,
    retryBtn: elements.retryBtn,
    restartBtn: elements.restartBtn,
    sfxToggleBtn: elements.sfxToggleBtn,
    crtToggleBtn: elements.crtToggleBtn
  });

  // Player manager - load saved state
  playerManager.loadFromStorage();

  // Set up cross-manager callbacks
  setupCallbacks();
}

/**
 * Set up callbacks between managers
 */
function setupCallbacks() {
  // Player -> Hazard: Check for barrel spawn on altitude change
  playerManager.onAltitudeChange = (altitude) => {
    if (hazardManager.shouldSpawn(altitude)) {
      hazardManager.trigger();
    }
  };

  // Player -> HUD: Update all HUD elements
  playerManager.onAltitudeChange = (altitude) => {
    hudManager.updateAltitude(altitude);
    hudManager.updateStory(altitude);
    hudManager.updateRank(altitude);

    // Check barrel spawn
    if (hazardManager.shouldSpawn(altitude)) {
      hazardManager.trigger();
    }
  };

  playerManager.onLaneChange = (lane, laneName) => {
    hudManager.updateLane(lane, laneName);
  };

  playerManager.onTorchChange = (current, max) => {
    hudManager.updateTorches(current, max);
  };

  playerManager.onCheckpointReached = (checkpoint) => {
    console.log(`Checkpoint reached: ${checkpoint}`);
    // Could show a visual notification here
  };

  playerManager.onGameStart = () => {
    hudManager.hideTitle();
    hudManager.hideGameOver();
    hazardManager.reset();
    frameManager.reset();
    frameManager.setFrame(CONFIG.FRAME_INDICES.DEFAULT, false);
  };

  playerManager.onGameOver = (reason) => {
    hudManager.showGameOver(reason);
    hazardManager.stop();
    frameManager.showDeathFrame();
  };

  playerManager.onCadenceUpdate = (cadence) => {
    hudManager.updateCadence(cadence);
  };

  // Hazard -> Player: Handle collision
  hazardManager.setCallbacks({
    onCollision: (barrelLane, hit) => {
      if (hit) {
        playerManager.loseTorch();
        // Show hit feedback
        if (elements.hazardAlert) {
          elements.hazardAlert.innerText = `⚠ STRUCK! LOST A TORCH (${playerManager.getTorches()} REMAINING)`;
          elements.hazardAlert.classList.remove('hidden');
          setTimeout(() => {
            elements.hazardAlert.classList.add('hidden');
          }, 1200);
        }
      } else {
        // Successful dodge - already handled by input manager
      }
    },
    onPassed: () => {
      // Barrel passed safely
    },
    onWarningStart: () => {
      // Warning started
    },
    onWarningEnd: () => {
      // Warning ended, barrel rolling
    }
  });

  // Input -> Game actions (already bound in input manager, but we can add extras)
  inputManager.onAscend = (delta) => {
    // Frame advance on step
    frameManager.advanceFrameIfNeeded(playerManager.getTargetAltitude());
    // Vertical bob
    frameManager.applyVerticalBob(playerManager.getTargetAltitude(), playerManager.isMoving());
  };

  inputManager.onDodge = (direction) => {
    // Lane shift visual handled in input manager
  };

  inputManager.onStartGame = () => {
    // Game started
  };

  inputManager.onResume = () => {
    hazardManager.reset();
    frameManager.setFrame(CONFIG.FRAME_INDICES.DEFAULT, true);
  };

  inputManager.onRestart = () => {
    hazardManager.reset();
    frameManager.reset();
    frameManager.setFrame(CONFIG.FRAME_INDICES.DEFAULT, false);
  };

  inputManager.onToggleSFX = (enabled) => {
    hudManager.updateSFXStatus(enabled);
  };

  inputManager.onToggleCRT = (enabled) => {
    hudManager.toggleCRT(enabled);
  };
}

/**
 * Main game loop
 */
function gameLoop(currentTime) {
  const dt = Math.min((currentTime - lastTime) / 1000, 0.1); // Cap at 100ms
  lastTime = currentTime;

  // Update systems
  inputManager.update(dt);
  playerManager.update(dt);

  // Update HUD (non-critical updates)
  if (playerManager.isGameStarted && !playerManager.isGameOver) {
    hudManager.updateAll(
      playerManager.getAltitude(),
      playerManager.getLane(),
      playerManager.getLaneName(),
      playerManager.getTorches(),
      playerManager.getMaxTorches(),
      playerManager.getCadence(),
      playerManager.isGameStarted,
      playerManager.isGameOver
    );
  }

  // Continue loop
  animationId = requestAnimationFrame(gameLoop);
}

/**
 * Handle window resize
 */
function handleResize() {
  // Frame manager handles canvas scaling in presentToScreen
  // But we may need to update UI overlay positions
  frameManager.applyVerticalBob(playerManager.getTargetAltitude(), playerManager.isMoving());
}

/**
 * Initialize the game
 */
async function init() {
  console.log('Initializing A Fool\'s Errand...');

  // Cache DOM
  cacheDOMElements();

  // Initialize managers
  initializeManagers();

  // Show title screen
  hudManager.showTitle();

  // Initial HUD state
  hudManager.updateAltitude(playerManager.getAltitude());
  hudManager.updateLane(playerManager.getLane(), playerManager.getLaneName());
  hudManager.updateStory(playerManager.getAltitude());
  hudManager.updateTorches(playerManager.getTorches(), playerManager.getMaxTorches());
  hudManager.updateRank(playerManager.getAltitude());
  hudManager.updateSFXStatus(playerManager.getSettings().sfxEnabled);
  hudManager.toggleCRT(playerManager.getSettings().crtEnabled);

  // Set up resize handler
  window.addEventListener('resize', handleResize);

  // Start game loop
  lastTime = performance.now();
  animationId = requestAnimationFrame(gameLoop);

  console.log('Game initialized successfully!');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Export for debugging
window.game = {
  player: playerManager,
  hazard: hazardManager,
  frame: frameManager,
  hud: hudManager,
  input: inputManager,
  audio: audioEngine,
  config: CONFIG
};