/**
 * A Fool's Errand - Procedural Frame Manager
 * Pure 1-bit canvas rendering with 2.5D spiral tower, walking animation, torchlight, and hazards
 */

import { CONFIG } from './config.js';

export class FrameManager {
  constructor() {
    // Virtual resolution for 1-bit rendering
    this.V_W = 230;
    this.V_H = 499;

    // Offscreen buffer for pure 1-bit rendering
    this.offscreen = document.createElement('canvas');
    this.offscreen.width = this.V_W;
    this.offscreen.height = this.V_H;
    this.bCtx = this.offscreen.getContext('2d', { willReadFrequently: true });

    // On-screen presentation canvas
    this.canvas = null;
    this.ctx = null;

    // 4x4 Bayer Dithering Matrix
    this.bayer4x4 = [
      [  0, 128,  32, 160],
      [192,  64, 224,  96],
      [ 48, 176,  16, 144],
      [240, 112, 208,  80]
    ];

    // Tower Geometry Constants
    this.TOWER_X = 118;
    this.TOWER_R = 50;
    this.STAIR_W = 34;
    this.PIXELS_PER_STEP = 11;
    this.STEPS_PER_TURN = 14;

    // Animation state
    this.time = 0;
    this.shakeTime = 0;
    this.shakeOffset = { x: 0, y: 0 };

    // Current render state (for interpolation)
    this.currentStep = 0;
    this.targetStep = 0;
    this.currentLane = 0;
    this.targetLane = 0;
    this.walkCycle = 0;
    this.velocity = 0;
    this.isMoving = false;

    // Barrel hazard state
    this.barrel = {
      active: false,
      step: 0,
      lane: 0,
      speed: 16.0,
      rotation: 0
    };

    // DOM elements
    this.gameCanvas = null;
    this.transitionOverlay = null;
    this.visualContainer = null;
  }

  // Initialize DOM references
  initDOM(gameCanvas, transitionOverlay, visualContainer) {
    this.gameCanvas = gameCanvas;
    this.transitionOverlay = transitionOverlay;
    this.visualContainer = visualContainer;

    // Set up presentation canvas
    this.canvas = this.gameCanvas;
    this.ctx = this.canvas.getContext('2d');
    this.canvas.width = this.V_W;
    this.canvas.height = this.V_H;

    // Initial render
    this.render(performance.now());
  }

  // Update render state from player manager
  updateRenderState(playerManager) {
    this.currentStep = playerManager.getAltitude();
    this.targetStep = playerManager.getTargetAltitude();
    this.currentLane = playerManager.getLane();
    this.targetLane = playerManager.getLane();
    this.walkCycle = playerManager.getWalkCycle();
    this.velocity = playerManager.getVelocity();
    this.isMoving = playerManager.isMoving();
  }

  // Update barrel state from hazard manager
  updateBarrelState(hazardManager) {
    this.barrel.active = hazardManager.isActive();
    this.barrel.step = hazardManager.getProgress() > 0 ? hazardManager.getProgress() * 100 : 0; // Approximate
    this.barrel.lane = hazardManager.getCurrentLane() || 0;

    // More accurate: get actual barrel data if exposed
    if (hazardManager._getBarrelData) {
      const data = hazardManager._getBarrelData();
      this.barrel.step = data.step;
      this.barrel.rotation = data.rotation;
      this.barrel.speed = data.speed;
    }
  }

  // Main render loop
  render(now) {
    const dt = Math.min(0.06, (now - (this.lastTime || now)) / 1000);
    this.lastTime = now;
    this.time += dt;

    // Smooth step interpolation for visual
    const diff = this.targetStep - this.currentStep;
    this.currentStep += diff * 12.0 * dt;

    // Smooth lane interpolation
    this.currentLane += (this.targetLane - this.currentLane) * 14.0 * dt;

    // Screen shake
    if (this.shakeTime > 0) {
      this.shakeTime -= dt;
      this.shakeOffset.x = (Math.random() - 0.5) * 8;
      this.shakeOffset.y = (Math.random() - 0.5) * 8;
    } else {
      this.shakeOffset.x = 0;
      this.shakeOffset.y = 0;
    }

    this._drawFrame();
    this._presentCanvas();
  }

  _drawFrame() {
    const b = this.bCtx;
    const w = this.V_W;
    const h = this.V_H;

    // Clear with deep black
    b.save();
    b.translate(this.shakeOffset.x, this.shakeOffset.y);
    b.fillStyle = '#000000';
    b.fillRect(-10, -10, w + 20, h + 20);

    const camStep = this.currentStep;
    const camY = Math.round(h * 0.56);

    // 1. Gothic Arch Window with Crescent Moon (Top-Left)
    this._drawArchWindow(b, camStep);

    // 2. Back-half of Spiral Staircase (behind tower)
    this._drawStairs(b, camStep, camY, false);

    // 3. Central Cylindrical Tower with Stone Masonry & Wall Sconces
    this._drawTowerCylinder(b, camStep, camY);

    // 4. Front-half of Spiral Staircase (in front of tower)
    this._drawStairs(b, camStep, camY, true);

    // 5. Rolling Barrel Hazard
    if (this.barrel.active) {
      this._drawBarrel(b, this.barrel, camStep, camY);
    }

    // 6. Dynamic 1-Bit Torchlight Radiance Halos
    this._drawTorchLights(b, camStep, camY);

    // 7. 1-Bit Bayer Matrix Dithering (Stipple rendering)
    this._applyBayerDither(b, w, h);

    // 8. Roland the Squire (Animated walking legs, cloak, torch with flickering fire)
    this._drawRoland(b, camStep, camY);

    b.restore();
  }

  _drawArchWindow(b, camStep) {
    const winX = 42;
    const winY = 110 + ((camStep * 1.5) % 320) - 80;
    if (winY < -60 || winY > this.V_H + 60) return;

    b.save();
    // Dark stone frame
    b.fillStyle = '#181818';
    b.beginPath();
    b.arc(winX, winY, 14, Math.PI, 0);
    b.lineTo(winX + 14, winY + 36);
    b.lineTo(winX - 14, winY + 36);
    b.closePath();
    b.fill();

    // Bright Moon
    b.fillStyle = '#ffffff';
    b.beginPath();
    b.arc(winX - 1, winY + 4, 11, 0, Math.PI * 2);
    b.fill();

    // Soft stippled moonlight beam
    const halo = b.createRadialGradient(winX, winY + 4, 11, winX, winY + 4, 46);
    halo.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
    halo.addColorStop(1, 'rgba(0, 0, 0, 0)');
    b.fillStyle = halo;
    b.beginPath();
    b.arc(winX, winY + 4, 46, 0, Math.PI * 2);
    b.fill();

    b.restore();
  }

  _drawTowerCylinder(b, camStep, camY) {
    b.save();
    const cx = this.TOWER_X;
    const r = this.TOWER_R;
    const leftX = cx - r;
    const rightX = cx + r;

    // Curved cylindrical shading
    const grad = b.createLinearGradient(leftX, 0, rightX, 0);
    grad.addColorStop(0.0, '#101010');
    grad.addColorStop(0.25, '#3c3c3c');
    grad.addColorStop(0.55, '#626262');
    grad.addColorStop(0.85, '#323232');
    grad.addColorStop(1.0, '#0c0c0c');

    b.fillStyle = grad;
    b.fillRect(leftX, 0, r * 2, this.V_H);

    // Horizontal stone course lines with continuous vertical scrolling
    b.strokeStyle = '#050505';
    b.lineWidth = 1;
    const blockH = 12;
    const scrollY = (camStep * this.PIXELS_PER_STEP) % blockH;

    for (let y = -blockH; y < this.V_H + blockH; y += blockH) {
      const lineY = Math.round(y + scrollY);
      b.beginPath();
      b.moveTo(leftX, lineY);
      b.lineTo(rightX, lineY);
      b.stroke();

      // Staggered vertical masonry notches
      const row = Math.floor((camStep * this.PIXELS_PER_STEP + y) / blockH);
      const shift = (row % 2) * 12;
      for (let bx = leftX + 8 + shift; bx < rightX - 4; bx += 20) {
        b.beginPath();
        b.moveTo(bx, lineY);
        b.lineTo(bx, lineY + blockH);
        b.stroke();
      }
    }

    // Wall-mounted iron torches with flickering flames
    const torchEvery = 14;
    const baseTorch = Math.floor((camStep - 20) / torchEvery) * torchEvery;
    for (let ts = baseTorch; ts < camStep + 25; ts += torchEvery) {
      const angle = -(ts / this.STEPS_PER_TURN) * Math.PI * 2;
      const cosA = Math.cos(angle);
      if (cosA > 0.2) {
        const sy = camY - (ts - camStep) * this.PIXELS_PER_STEP;
        const sx = cx + Math.sin(angle) * (r - 2);

        // Iron wall sconce
        b.fillStyle = '#080808';
        b.fillRect(sx - 2, sy - 8, 4, 12);

        // Flickering flame
        b.fillStyle = '#ffffff';
        b.beginPath();
        b.moveTo(sx - 2, sy - 8);
        b.lineTo(sx, sy - 15 - Math.sin(this.time * 24 + ts) * 3);
        b.lineTo(sx + 2, sy - 8);
        b.closePath();
        b.fill();
      }
    }

    b.restore();
  }

  _drawStairs(b, camStep, camY, renderFront) {
    b.save();
    const range = 22;
    const minS = Math.floor(camStep - range);
    const maxS = Math.ceil(camStep + range);

    for (let s = minS; s <= maxS; s++) {
      const delta = s - camStep;
      const y = camY - delta * this.PIXELS_PER_STEP;

      const angle = -(s / this.STEPS_PER_TURN) * Math.PI * 2;
      const sinA = Math.sin(angle);
      const cosA = Math.cos(angle);

      const innerX = this.TOWER_X + sinA * this.TOWER_R;
      const outerX = this.TOWER_X + sinA * (this.TOWER_R + this.STAIR_W);

      const isFront = cosA >= -0.15;
      if (isFront !== renderFront) continue;

      const light = Math.max(0.18, (cosA + 1.0) * 0.45);
      const shade = Math.floor(light * 220);
      const stepThick = 5;

      // Stone Step Tread & Riser
      b.fillStyle = renderFront ? `rgb(${shade}, ${shade}, ${shade})` : '#161616';
      b.strokeStyle = '#050505';
      b.lineWidth = 1;

      b.beginPath();
      b.moveTo(innerX, y);
      b.lineTo(outerX, y);
      b.lineTo(outerX, y + stepThick);
      b.lineTo(innerX, y + stepThick);
      b.closePath();
      b.fill();
      b.stroke();

      if (renderFront) {
        // Bright Top Tread Edge
        b.strokeStyle = `rgb(${Math.min(255, shade + 45)}, ${Math.min(255, shade + 45)}, ${Math.min(255, shade + 45)})`;
        b.beginPath();
        b.moveTo(innerX, y);
        b.lineTo(outerX, y);
        b.stroke();

        // Under-step support corbel
        b.fillStyle = '#1a1a1a';
        b.fillRect(Math.min(innerX, outerX) + 6, y + stepThick, 6, 4);
      }
    }
    b.restore();
  }

  // Compute 3D Cylindrical Coordinates for any step
  _getStepCoords(s, camStep, camY, laneOffset = 0) {
    const delta = s - camStep;
    const y = camY - delta * this.PIXELS_PER_STEP;

    // Spiral wraps around the cylinder (counter-clockwise ascending)
    const angle = -(s / this.STEPS_PER_TURN) * Math.PI * 2;
    const sinA = Math.sin(angle);
    const cosA = Math.cos(angle);

    const radius = this.TOWER_R + this.STAIR_W * 0.5 + laneOffset * 9;
    const x = this.TOWER_X + sinA * radius;

    return {
      x: Math.round(x),
      y: Math.round(y),
      z: cosA,
      sinA,
      cosA,
      isFront: cosA >= -0.15
    };
  }

  _drawBarrel(b, barrel, camStep, camY) {
    // Get barrel position - we need actual barrel step from hazard manager
    // For now, use the interpolated position
    const barrelStep = barrel.step;
    const coords = this._getStepCoords(barrelStep, camStep, camY, barrel.lane);
    if (!coords.isFront && coords.z < -0.3) return;

    b.save();
    b.translate(coords.x, coords.y - 7);
    b.rotate(barrel.rotation);

    const br = 8;
    // Barrel Body
    b.fillStyle = '#ffffff';
    b.strokeStyle = '#000000';
    b.lineWidth = 1.5;
    b.beginPath();
    b.arc(0, 0, br, 0, Math.PI * 2);
    b.fill();
    b.stroke();

    // Wooden Staves & Iron Hoops
    b.fillStyle = '#000000';
    b.beginPath();
    b.arc(0, 0, br * 0.65, 0, Math.PI * 2);
    b.fill();

    b.fillStyle = '#ffffff';
    b.fillRect(-br, -1, br * 2, 2);
    b.fillRect(-1, -br, 2, br * 2);

    b.restore();
  }

  _drawTorchLights(b, camStep, camY) {
    b.save();

    // 1. Roland's Torch Light Halo
    const rolandPos = this._getStepCoords(camStep, camStep, camY, this.currentLane);
    const tx = rolandPos.x - 8;
    const ty = rolandPos.y - 18;
    const flicker = Math.sin(this.time * 20) * 2.5 + Math.cos(this.time * 33) * 1.5;
    const radius = 68 + flicker;

    const torchGrad = b.createRadialGradient(tx, ty, 4, tx, ty, radius);
    torchGrad.addColorStop(0.0, 'rgba(255, 255, 255, 0.95)');
    torchGrad.addColorStop(0.35, 'rgba(215, 215, 215, 0.65)');
    torchGrad.addColorStop(0.7, 'rgba(110, 110, 110, 0.25)');
    torchGrad.addColorStop(1.0, 'rgba(0, 0, 0, 0)');

    b.globalCompositeOperation = 'screen';
    b.fillStyle = torchGrad;
    b.beginPath();
    b.arc(tx, ty, radius, 0, Math.PI * 2);
    b.fill();

    // 2. Wall Sconce Torches Halos
    const torchEvery = 14;
    const baseTorch = Math.floor((camStep - 15) / torchEvery) * torchEvery;
    for (let ts = baseTorch; ts < camStep + 18; ts += torchEvery) {
      const angle = -(ts / this.STEPS_PER_TURN) * Math.PI * 2;
      if (Math.cos(angle) > 0.2) {
        const sy = camY - (ts - camStep) * this.PIXELS_PER_STEP;
        const sx = this.TOWER_X + Math.sin(angle) * (this.TOWER_R - 2);

        const wGrad = b.createRadialGradient(sx, sy - 15, 3, sx, sy - 15, 38);
        wGrad.addColorStop(0.0, 'rgba(255, 255, 255, 0.7)');
        wGrad.addColorStop(1.0, 'rgba(0, 0, 0, 0)');
        b.fillStyle = wGrad;
        b.beginPath();
        b.arc(sx, sy - 15, 38, 0, Math.PI * 2);
        b.fill();
      }
    }

    b.restore();
  }

  // 1-Bit Bayer Matrix Dithering
  _applyBayerDither(b, w, h) {
    const imgData = b.getImageData(0, 0, w, h);
    const d = imgData.data;
    const bayer = this.bayer4x4;

    for (let y = 0; y < h; y++) {
      const row = y * w * 4;
      const bRow = bayer[y % 4];

      for (let x = 0; x < w; x++) {
        const i = row + (x * 4);
        const gray = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
        const threshold = bRow[x % 4];

        const val = gray >= threshold ? 255 : 0;
        d[i] = val;
        d[i + 1] = val;
        d[i + 2] = val;
        d[i + 3] = 255;
      }
    }

    b.putImageData(imgData, 0, 0);
  }

  // Roland Sprite (Facing left, climbing the stairs with torch)
  _drawRoland(b, camStep, camY) {
    const pos = this._getStepCoords(camStep, camStep, camY, this.currentLane);

    b.save();
    b.translate(pos.x, pos.y);

    // Facing left towards ascending stairs
    b.scale(-1, 1);

    const isMoving = this.isMoving;
    const walkPhase = Math.sin(this.walkCycle * Math.PI * 2);

    let frontLegY = 0;
    let backLegY = 0;
    let bodyBob = 0;

    if (isMoving) {
      frontLegY = Math.max(0, walkPhase * 6);
      backLegY = Math.max(0, -walkPhase * 4);
      bodyBob = Math.abs(walkPhase) * 2.5;
    }

    // Step Shadow
    b.fillStyle = '#000000';
    b.fillRect(-7, 0, 14, 2);

    // 1. Back Leg
    b.fillStyle = '#000000';
    b.fillRect(-5, -8 + backLegY - bodyBob, 3.5, 8 - backLegY);

    // 2. Front Leg stepping onto stone riser
    b.fillRect(1, -8 - frontLegY - bodyBob, 4, 8 + frontLegY);

    // 3. Cloak behind back
    b.fillStyle = '#000000';
    b.beginPath();
    b.moveTo(-6, -20 - bodyBob);
    b.lineTo(-12, -13 - bodyBob);
    b.lineTo(-6, -7 - bodyBob);
    b.closePath();
    b.fill();

    // 4. White Tunic with bold contour
    b.fillStyle = '#ffffff';
    b.strokeStyle = '#000000';
    b.lineWidth = 1.5;
    b.beginPath();
    b.roundRect(-5, -19 - bodyBob, 10, 12, [3, 3, 0, 0]);
    b.fill();
    b.stroke();

    // Leather Belt
    b.fillStyle = '#000000';
    b.fillRect(-5, -10 - bodyBob, 10, 2);

    // 5. Squire Hood
    b.fillStyle = '#000000';
    b.beginPath();
    b.arc(0, -23 - bodyBob, 5.5, 0, Math.PI * 2);
    b.fill();

    b.beginPath();
    b.moveTo(-4, -22 - bodyBob);
    b.lineTo(-9, -20 - bodyBob);
    b.lineTo(-4, -18 - bodyBob);
    b.closePath();
    b.fill();

    // 6. Face Profile & Eye
    b.fillStyle = '#ffffff';
    b.beginPath();
    b.arc(2, -23 - bodyBob, 3.5, -Math.PI * 0.45, Math.PI * 0.45);
    b.lineTo(1, -19 - bodyBob);
    b.closePath();
    b.fill();

    b.fillStyle = '#000000';
    b.fillRect(3.5, -24 - bodyBob, 1.5, 1.5);

    // 7. Arm Holding Wooden Torch
    b.fillStyle = '#ffffff';
    b.fillRect(2, -16 - bodyBob, 6, 4);
    b.strokeStyle = '#000000';
    b.lineWidth = 1;
    b.strokeRect(2, -16 - bodyBob, 6, 4);

    // Torch Stick
    const torchX = 8;
    const torchY = -15 - bodyBob;
    b.fillStyle = '#000000';
    b.fillRect(torchX, torchY - 8, 2.5, 12);

    // 8. Burning Flame with dynamic flicker
    const flameH = 8 + Math.sin(this.time * 25) * 3 + Math.random() * 2;
    b.fillStyle = '#ffffff';
    b.strokeStyle = '#000000';
    b.lineWidth = 1;
    b.beginPath();
    b.moveTo(torchX - 2, torchY - 8);
    b.lineTo(torchX + 1.25, torchY - 8 - flameH);
    b.lineTo(torchX + 4.5, torchY - 8);
    b.closePath();
    b.fill();
    b.stroke();

    b.restore();
  }

  // Scales Offscreen Buffer onto Main Canvas
  _presentCanvas() {
    const stage = document.getElementById('game-stage');
    if (!stage) return;
    const rect = stage.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    if (this.canvas.width !== this.V_W || this.canvas.height !== this.V_H) {
      this.canvas.width = this.V_W;
      this.canvas.height = this.V_H;
    }

    this.ctx.imageSmoothingEnabled = false;
    this.ctx.drawImage(this.offscreen, 0, 0);
  }

  // =========================================================================
  // PUBLIC API (compatible with old frame manager interface)
  // =========================================================================

  setFrame(index, animate = true) {
    // No-op for procedural rendering - frames are computed from game state
  }

  advanceFrameIfNeeded(currentStep) {
    // No-op - animation is continuous in render loop
  }

  showBarrelFrame() {
    // Visual feedback handled by hazard alert banner
  }

  showBarrelActiveFrame() {
    // Visual feedback handled by hazard alert banner
  }

  showAftermathFrame() {
    // Visual feedback handled by hazard alert banner
  }

  showDeathFrame() {
    this.shakeTime = 0.4;
  }

  reset() {
    this.currentStep = 0;
    this.targetStep = 0;
    this.currentLane = 0;
    this.targetLane = 0;
    this.walkCycle = 0;
    this.velocity = 0;
    this.isMoving = false;
    this.barrel = {
      active: false,
      step: 0,
      lane: 0,
      speed: 16.0,
      rotation: 0
    };
    this.shakeTime = 0;
  }

  applyVerticalBob(currentStep, isMoving) {
    // Handled in render loop
  }

  applyLaneShift(lane, animate = true) {
    this.targetLane = lane;
  }

  returnToCenter() {
    this.targetLane = 0;
  }

  shake(intensity = CONFIG.EFFECTS.SCREEN_SHAKE_INTENSITY, duration = CONFIG.EFFECTS.SCREEN_SHAKE_DURATION) {
    this.shakeTime = duration / 1000;
  }

  getCurrentIndex() {
    return 0;
  }
}

// Singleton instance
export const frameManager = new FrameManager();