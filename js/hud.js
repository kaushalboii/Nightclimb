/**
 * A Fool's Errand - HUD Manager
 * Handles all UI updates: altitude, lane, torches, story, rank, cadence
 */

import { CONFIG, getStoryBeat, getRank } from './config.js';

export class HUDManager {
  constructor() {
    // DOM Elements
    this.altitudeDisplay = null;
    this.laneIndicator = null;
    this.actIndicator = null;
    this.poemText = null;
    this.torchesCount = null;
    this.speedMeter = null;
    this.rankTitle = null;
    this.titleOverlay = null;
    this.gameOverOverlay = null;
    this.gameOverReason = null;
    this.dodgeTag = null;
    this.sfxStatus = null;
    this.scanlineOverlay = null;
    this.crtToggleBtn = null;

    // State
    this.currentAct = '';
    this.currentPoem = '';
  }

  // Initialize DOM references
  initDOM(elements) {
    this.altitudeDisplay = elements.altitudeDisplay;
    this.laneIndicator = elements.laneIndicator;
    this.actIndicator = elements.actIndicator;
    this.poemText = elements.poemText;
    this.torchesCount = elements.torchesCount;
    this.speedMeter = elements.speedMeter;
    this.rankTitle = elements.rankTitle;
    this.titleOverlay = elements.titleOverlay;
    this.gameOverOverlay = elements.gameOverOverlay;
    this.gameOverReason = elements.gameOverReason;
    this.dodgeTag = elements.dodgeTag;
    this.sfxStatus = elements.sfxStatus;
    this.scanlineOverlay = elements.scanlineOverlay;
    this.crtToggleBtn = elements.crtToggleBtn;
    this.flagSteps = elements.flagSteps;
  }

  // Update altitude display
  updateAltitude(altitude) {
    if (this.altitudeDisplay) {
      this.altitudeDisplay.innerHTML = `${altitude} <span class="text-[12px]">♠</span>`;
    }
    if (this.flagSteps) {
      this.flagSteps.innerText = altitude.toString();
    }
  }

  // Update lane indicator
  updateLane(lane, laneName) {
    if (this.laneIndicator) {
      this.laneIndicator.innerText = laneName;

      // Flash effect
      this.laneIndicator.classList.add('bg-white', 'text-black');
      setTimeout(() => {
        this.laneIndicator.classList.remove('bg-white', 'text-black');
      }, CONFIG.EFFECTS.LANE_INDICATOR_FLASH_MS);
    }
  }

  // Update story act and poem
  updateStory(altitude) {
    const beat = getStoryBeat(altitude);

    if (beat.act !== this.currentAct && this.actIndicator) {
      this.currentAct = beat.act;
      this.actIndicator.innerHTML = beat.act;
    }

    if (beat.poem !== this.currentPoem && this.poemText) {
      this.currentPoem = beat.poem;
      this.poemText.innerHTML = `&ldquo;${beat.poem}&rdquo;`;
    }
  }

  // Update torch count
  updateTorches(current, max) {
    if (this.torchesCount) {
      this.torchesCount.innerText = `${current}/${max}`;
    }
  }

  // Update cadence/speed meter
  updateCadence(stepsPerSec) {
    if (this.speedMeter) {
      this.speedMeter.innerText = `CADENCE: ${stepsPerSec} STEPS/SEC`;
    }
  }

  // Update rank title
  updateRank(altitude) {
    if (this.rankTitle) {
      this.rankTitle.innerText = getRank(altitude);
    }
  }

  // Show dodge feedback
  showDodgeFeedback(direction) {
    if (!this.dodgeTag) return;

    const messages = {
      [CONFIG.LANES.LEFT]: 'EVADED LEFT',
      [CONFIG.LANES.RIGHT]: 'EVADED RIGHT',
      [CONFIG.LANES.MID]: 'CENTERED'
    };

    this.dodgeTag.innerText = messages[direction] || 'EVADED!';
    this.dodgeTag.style.opacity = '1';

    // Trigger animation
    this.dodgeTag.classList.remove('show');
    void this.dodgeTag.offsetWidth; // Force reflow
    this.dodgeTag.classList.add('show');

    setTimeout(() => {
      this.dodgeTag.style.opacity = '0';
      this.dodgeTag.classList.remove('show');
    }, CONFIG.EFFECTS.DODGE_TAG_DURATION);
  }

  // Show title screen
  showTitle() {
    if (this.titleOverlay) {
      this.titleOverlay.classList.remove('hidden');
    }
    if (this.gameOverOverlay) {
      this.gameOverOverlay.classList.add('hidden');
    }
  }

  // Hide title screen
  hideTitle() {
    if (this.titleOverlay) {
      this.titleOverlay.classList.add('hidden');
    }
  }

  // Show game over
  showGameOver(reason) {
    if (this.gameOverOverlay) {
      this.gameOverOverlay.classList.remove('hidden');
    }
    if (this.gameOverReason) {
      this.gameOverReason.innerText = reason;
    }
    if (this.titleOverlay) {
      this.titleOverlay.classList.add('hidden');
    }
  }

  // Hide game over
  hideGameOver() {
    if (this.gameOverOverlay) {
      this.gameOverOverlay.classList.add('hidden');
    }
  }

  // Update SFX toggle button
  updateSFXStatus(enabled) {
    if (this.sfxStatus) {
      this.sfxStatus.innerText = enabled ? 'ON' : 'OFF';
      this.sfxStatus.className = enabled ? 'text-white' : 'text-red-400';
    }
  }

  // Toggle CRT scanlines
  toggleCRT(enabled) {
    if (this.scanlineOverlay) {
      this.scanlineOverlay.classList.toggle('hidden', !enabled);
    }
  }

  // Full HUD update (called each frame)
  updateAll(altitude, lane, laneName, torches, maxTorches, cadence, isGameStarted, isGameOver) {
    if (isGameOver) return;

    this.updateAltitude(altitude);
    this.updateLane(lane, laneName);
    this.updateStory(altitude);
    this.updateTorches(torches, maxTorches);
    this.updateCadence(cadence);
    this.updateRank(altitude);
  }

  // Show hazard alert with custom message
  showHazardAlert(message) {
    // This is handled by hazard manager, but we could extend here
  }
}

// Singleton instance
export const hudManager = new HUDManager();