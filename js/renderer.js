// Pixel-Perfect 1-Bit Monochrome Renderer for Nightclimb
// Exact recreation of "A Fool's Errand" (IORAMA)

class TowerRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');

    // Fixed virtual resolution: 240x480 (Exact Playdate / retro handheld aspect ratio)
    this.vW = 240;
    this.vH = 480;

    // Offscreen 1-bit rendering buffer
    this.buffer = document.createElement('canvas');
    this.buffer.width = this.vW;
    this.buffer.height = this.vH;
    this.bCtx = this.buffer.getContext('2d', { willReadFrequently: true });

    // 4x4 Bayer Dithering Matrix
    this.bayer4x4 = [
      [  0, 128,  32, 160],
      [192,  64, 224,  96],
      [ 48, 176,  16, 144],
      [240, 112, 208,  80]
    ];

    // Geometry parameters (matches screenshots)
    this.towerX = 142; // Center of tower cylinder
    this.towerR = 64;  // Radius of tower
    this.stairW = 34;  // Width of staircase steps
    this.pixelsPerStep = 18; // Height per step
    this.stepsPerTurn = 16;  // Steps per 360 degree rotation

    this.time = 0;
    this.torchFlicker = 0;
    this.shake = 0;

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.ctx.imageSmoothingEnabled = false;
  }

  addShake(amount) {
    this.shake = Math.max(this.shake, amount);
  }

  render(player, obstacleManager, dt) {
    this.time += dt;
    this.torchFlicker = (Math.sin(this.time * 22) * 2 + Math.cos(this.time * 37) * 1.5);

    if (this.shake > 0) {
      this.shake = Math.max(0, this.shake - dt * 25);
    }

    const b = this.bCtx;
    const w = this.vW;
    const h = this.vH;

    // 1. Clear buffer with solid black
    b.fillStyle = '#000000';
    b.fillRect(0, 0, w, h);

    const camStep = player.altitude * 5.0; // Current step coordinate
    const camY = h * 0.62; // Roland's fixed screen Y position

    // 2. Draw Gothic Arch Window with Crescent Moon (Top Left, like screenshots 3 & 4)
    this.drawMoonWindow(b, camStep);

    // 3. Draw Tower Background & Back-half of spiral stairs
    this.drawTowerAndStairs(b, camStep, camY, false);

    // 4. Draw Central Cylindrical Stone Tower
    this.drawTowerCylinder(b, camStep, camY);

    // 5. Draw Front-half of spiral stairs
    this.drawTowerAndStairs(b, camStep, camY, true);

    // 6. Draw Traps (Rolling Barrels, Spikes, Pendulums)
    this.drawTraps(b, obstacleManager.obstacles, camStep, camY);

    // 7. Apply Dithered Torchlight & Wall Sconces
    this.drawLightCones(b, camStep, camY, player);

    // 8. 1-BIT QUANTIZATION PASS (Turn background & lights into authentic stippled dithering)
    this.applyBayerDither(b, w, h);

    // 9. Draw Roland The Squire Sprite ON TOP (Guarantees crispness, never washed out!)
    this.drawRoland(b, player, camY);

    // 10. Draw Screen HUD Elements directly into pixel buffer (Shield in top-left!)
    this.drawPixelHUD(b, player);

    // 11. Render scaled onto main screen with strict aspect ratio preservation (Square Pixels!)
    this.presentToScreen();
  }

  // Draw the Arch Window & Moon from Screenshot 3 & 4
  drawMoonWindow(b, camStep) {
    const winX = 36;
    // Window scrolls slowly with parallax
    const winY = 60 + ((camStep * 2.5) % 360) - 60;
    if (winY < -80 || winY > this.vH + 80) return;

    b.save();
    // Arch frame
    b.fillStyle = '#1c1c1c';
    b.beginPath();
    b.arc(winX, winY, 16, Math.PI, 0);
    b.lineTo(winX + 16, winY + 36);
    b.lineTo(winX - 16, winY + 36);
    b.closePath();
    b.fill();

    // Glowing Moon
    b.fillStyle = '#ffffff';
    b.beginPath();
    b.arc(winX, winY + 4, 12, 0, Math.PI * 2);
    b.fill();

    // Moonlight halo (grayscale for dithering)
    const halo = b.createRadialGradient(winX, winY + 4, 12, winX, winY + 4, 42);
    halo.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
    halo.addColorStop(1, 'rgba(0, 0, 0, 0)');
    b.fillStyle = halo;
    b.beginPath();
    b.arc(winX, winY + 4, 42, 0, Math.PI * 2);
    b.fill();

    b.restore();
  }

  // Draw the Cylindrical Stone Tower
  drawTowerCylinder(b, camStep, camY) {
    b.save();
    const cx = this.towerX;
    const r = this.towerR;
    const leftX = cx - r;
    const rightX = cx + r;

    // Curved cylinder grayscale gradient
    const grad = b.createLinearGradient(leftX, 0, rightX, 0);
    grad.addColorStop(0.0, '#101010');
    grad.addColorStop(0.25, '#353535');
    grad.addColorStop(0.55, '#5a5a5a');
    grad.addColorStop(0.85, '#2e2e2e');
    grad.addColorStop(1.0, '#0a0a0a');

    b.fillStyle = grad;
    b.fillRect(leftX, 0, r * 2, this.vH);

    // Stone masonry courses (individual blocks with vertical scroll)
    b.strokeStyle = '#050505';
    b.lineWidth = 1;
    const blockH = 14;
    const blockScroll = (camStep * this.pixelsPerStep) % blockH;

    for (let y = -blockH; y < this.vH + blockH; y += blockH) {
      const lineY = Math.round(y + blockScroll);
      b.beginPath();
      b.moveTo(leftX, lineY);
      b.lineTo(rightX, lineY);
      b.stroke();

      // Vertical block lines
      const rowIdx = Math.floor((camStep * this.pixelsPerStep + y) / blockH);
      const rowShift = (rowIdx % 2) * 16;
      for (let bx = leftX + 10 + rowShift; bx < rightX - 4; bx += 24) {
        b.beginPath();
        b.moveTo(bx, lineY);
        b.lineTo(bx, lineY + blockH);
        b.stroke();
      }
    }

    // Wall-mounted iron torch sconces
    const torchEvery = 14; // Every 14 steps
    const baseTorchStep = Math.floor((camStep - 20) / torchEvery) * torchEvery;
    for (let ts = baseTorchStep; ts < camStep + 25; ts += torchEvery) {
      const theta = (ts / this.stepsPerTurn) * Math.PI * 2;
      const cosT = Math.cos(theta);
      if (cosT > 0.2) {
        const sy = camY - (ts - camStep) * this.pixelsPerStep;
        const sx = cx + Math.sin(theta) * (r - 2);

        // Torch mount
        b.fillStyle = '#050505';
        b.fillRect(sx - 2, sy - 8, 4, 12);
        // Torch flame
        b.fillStyle = '#ffffff';
        b.beginPath();
        b.moveTo(sx - 2, sy - 8);
        b.lineTo(sx, sy - 16 - Math.random() * 3);
        b.lineTo(sx + 2, sy - 8);
        b.closePath();
        b.fill();
      }
    }

    b.restore();
  }

  // Calculate 2.5D position for a step on the spiral
  getStepCoords(stepIndex, camStep, camY, radialOffset = 0) {
    const delta = stepIndex - camStep;
    const y = camY - delta * this.pixelsPerStep;

    const angle = (stepIndex / this.stepsPerTurn) * Math.PI * 2;
    const sinA = Math.sin(angle);
    const cosA = Math.cos(angle);

    const radius = this.towerR + radialOffset;
    const x = this.towerX + sinA * radius;

    return {
      x: Math.round(x),
      y: Math.round(y),
      z: cosA,
      isFront: cosA >= -0.15
    };
  }

  // Draw Spiral Stone Stairs wrapping around tower
  drawTowerAndStairs(b, camStep, camY, renderFront) {
    b.save();

    const range = 24; // steps above and below camera
    const minStep = Math.floor(camStep - range);
    const maxStep = Math.ceil(camStep + range);

    for (let s = minStep; s <= maxStep; s++) {
      const inner = this.getStepCoords(s, camStep, camY, 0);
      const outer = this.getStepCoords(s, camStep, camY, this.stairW);

      const isFront = (inner.z + outer.z) * 0.5 >= -0.12;
      if (isFront !== renderFront) continue;

      const light = Math.max(0.2, (inner.z + 1.0) * 0.45);
      const shade = Math.floor(light * 220);

      const stepThick = 6;

      // Step stone block
      b.fillStyle = renderFront ? `rgb(${shade}, ${shade}, ${shade})` : '#151515';
      b.strokeStyle = '#050505';
      b.lineWidth = 1;

      b.beginPath();
      b.moveTo(inner.x, inner.y);
      b.lineTo(outer.x, outer.y);
      b.lineTo(outer.x, outer.y + stepThick);
      b.lineTo(inner.x, inner.y + stepThick);
      b.closePath();
      b.fill();
      b.stroke();

      // Step top edge highlight
      if (renderFront) {
        b.strokeStyle = `rgb(${Math.min(255, shade + 50)}, ${Math.min(255, shade + 50)}, ${Math.min(255, shade + 50)})`;
        b.beginPath();
        b.moveTo(inner.x, inner.y);
        b.lineTo(outer.x, outer.y);
        b.stroke();
      }
    }

    b.restore();
  }

  // Draw Traps (Rolling Powder Keg Barrel, Spikes, Ghosts, Crumbling steps)
  drawTraps(b, obstacles, camStep, camY) {
    for (const obs of obstacles) {
      const stepIdx = obs.altitude * 5.0;
      const p = this.getStepCoords(stepIdx, camStep, camY, this.stairW * 0.5);

      if (p.y < -40 || p.y > this.vH + 40) continue;

      b.save();
      b.translate(p.x, p.y);

      if (obs.type === 'BARREL') {
        // Rolling Powder Keg / Barrel (Screenshot 2)
        b.rotate(obs.angle);
        b.fillStyle = '#ffffff';
        b.strokeStyle = '#000000';
        b.lineWidth = 1.5;

        // Barrel cylinder body
        b.beginPath();
        b.roundRect(-10, -7, 20, 14, 3);
        b.fill();
        b.stroke();

        // Iron hoops on barrel
        b.strokeStyle = '#000000';
        b.strokeRect(-6, -7, 3, 14);
        b.strokeRect(3, -7, 3, 14);

        // Fuse on barrel
        b.beginPath();
        b.moveTo(0, -7);
        b.lineTo(3, -12);
        b.stroke();
        // Spark
        b.fillStyle = '#ffffff';
        b.fillRect(2, -14, 2, 2);

      } else if (obs.type === 'GHOST') {
        // Floating Spire Wraith (Screenshot 4)
        const bobY = Math.sin(obs.bobTimer) * 4;
        b.translate(0, -18 + bobY);

        b.fillStyle = '#ffffff';
        b.strokeStyle = '#000000';
        b.lineWidth = 1.5;

        // Ghost body sheet
        b.beginPath();
        b.arc(0, -6, 7, Math.PI, 0);
        b.lineTo(7, 6);
        b.lineTo(3, 4);
        b.lineTo(0, 6);
        b.lineTo(-4, 4);
        b.lineTo(-7, 6);
        b.closePath();
        b.fill();
        b.stroke();

        // Dark hollow eyes
        b.fillStyle = '#000000';
        b.fillRect(-4, -6, 2, 4);
        b.fillRect(2, -6, 2, 4);

      } else if (obs.type === 'SPIKE') {
        // Base plate
        b.fillStyle = '#111111';
        b.strokeStyle = '#ffffff';
        b.strokeRect(-9, -2, 18, 4);

        if (obs.spikeHeight > 0.05) {
          const h = 12 * obs.spikeHeight;
          b.fillStyle = '#ffffff';
          b.strokeStyle = '#000000';
          b.lineWidth = 1;
          [-6, 0, 6].forEach(sx => {
            b.beginPath();
            b.moveTo(sx - 2, -2);
            b.lineTo(sx, -2 - h);
            b.lineTo(sx + 2, -2);
            b.closePath();
            b.fill();
            b.stroke();
          });
        }
      } else if (obs.type === 'CRUMBLE') {
        if (!obs.isCollapsed) {
          b.translate(obs.shakeOffset * 0.4, 0);
          b.fillStyle = '#444444';
          b.strokeStyle = '#000000';
          b.fillRect(-10, -3, 20, 6);
          b.strokeRect(-10, -3, 20, 6);
        } else {
          b.fillStyle = '#000000';
          b.fillRect(-9, -2, 18, 4);
        }
      }

      b.restore();
    }
  }

  // Draw Light Radiance before dithering
  drawLightCones(b, camStep, camY, player) {
    b.save();

    // 1. Roland's Torch Glow
    const rolandPos = this.getStepCoords(camStep, camStep, camY, this.stairW * 0.5);
    const tx = rolandPos.x + 6 * player.direction;
    const ty = rolandPos.y - 18;
    const r = 62 + this.torchFlicker;

    const torchGrad = b.createRadialGradient(tx, ty, 4, tx, ty, r);
    torchGrad.addColorStop(0.0, 'rgba(255, 255, 255, 0.95)');
    torchGrad.addColorStop(0.35, 'rgba(220, 220, 220, 0.65)');
    torchGrad.addColorStop(0.7, 'rgba(110, 110, 110, 0.25)');
    torchGrad.addColorStop(1.0, 'rgba(0, 0, 0, 0)');

    b.globalCompositeOperation = 'screen';
    b.fillStyle = torchGrad;
    b.beginPath();
    b.arc(tx, ty, r, 0, Math.PI * 2);
    b.fill();

    b.restore();
  }

  // 1-Bit Bayer Matrix Quantization Filter
  applyBayerDither(b, w, h) {
    const imgData = b.getImageData(0, 0, w, h);
    const d = imgData.data;
    const bayer = this.bayer4x4;

    for (let y = 0; y < h; y++) {
      const rowOffset = y * w * 4;
      const bayerRow = bayer[y % 4];

      for (let x = 0; x < w; x++) {
        const i = rowOffset + (x * 4);
        const gray = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
        const threshold = bayerRow[x % 4];

        const val = gray >= threshold ? 255 : 0;
        d[i] = val;
        d[i + 1] = val;
        d[i + 2] = val;
        d[i + 3] = 255;
      }
    }

    b.putImageData(imgData, 0, 0);
  }

  // Draw Roland the Squire Sprite (Crisp, High-Contrast, Never Washed Out!)
  drawRoland(b, player, camY) {
    const camStep = player.altitude * 5.0;
    const pos = this.getStepCoords(camStep, camStep, camY, this.stairW * 0.5);

    b.save();
    b.translate(pos.x, pos.y);
    b.scale(player.direction, 1);

    if (player.isAlive) {
      const isMoving = Math.abs(player.velocity) > 0.05;
      const walkPhase = Math.sin(player.walkCycle * Math.PI * 2);

      // Shadow on current step
      b.fillStyle = '#000000';
      b.fillRect(-7, 0, 14, 2);

      // Back leg & Front leg animation
      let frontLegY = 0;
      let backLegY = 0;
      let bodyBob = 0;

      if (isMoving) {
        // Front leg lifts up to step onto next stair
        frontLegY = Math.max(0, walkPhase * 5);
        backLegY = Math.max(0, -walkPhase * 3);
        bodyBob = Math.abs(walkPhase) * 2;
      }

      // 1. Back leg (Solid black)
      b.fillStyle = '#000000';
      b.fillRect(-5, -8 + backLegY - bodyBob, 3, 8 - backLegY);

      // 2. Front leg stepping up
      b.fillRect(1, -8 - frontLegY - bodyBob, 4, 8 + frontLegY);

      // 3. Dark Cloak / Pack behind body
      b.fillStyle = '#000000';
      b.beginPath();
      b.moveTo(-6, -20 - bodyBob);
      b.lineTo(-12, -13 - bodyBob);
      b.lineTo(-6, -7 - bodyBob);
      b.closePath();
      b.fill();

      // 4. White Tunic (Bright crisp white, bold black contour)
      b.fillStyle = '#ffffff';
      b.strokeStyle = '#000000';
      b.lineWidth = 1.5;
      b.beginPath();
      b.roundRect(-5, -19 - bodyBob, 10, 12, [3, 3, 0, 0]);
      b.fill();
      b.stroke();

      // Belt
      b.fillStyle = '#000000';
      b.fillRect(-5, -10 - bodyBob, 10, 2);

      // 5. Squire Hood (Black)
      b.fillStyle = '#000000';
      b.beginPath();
      b.arc(0, -23 - bodyBob, 5.5, 0, Math.PI * 2);
      b.fill();

      // Pointy hood back
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

      // Eye dot
      b.fillStyle = '#000000';
      b.fillRect(3.5, -24 - bodyBob, 1.5, 1.5);

      // 7. Arm reaching forward holding Wooden Torch
      b.fillStyle = '#ffffff';
      b.fillRect(2, -16 - bodyBob, 6, 4);
      b.strokeStyle = '#000000';
      b.lineWidth = 1;
      b.strokeRect(2, -16 - bodyBob, 6, 4);

      // Torch Stick (Black wood)
      const torchX = 8;
      const torchY = -15 - bodyBob;
      b.fillStyle = '#000000';
      b.fillRect(torchX, torchY - 8, 2.5, 12);

      // 8. Burning Flame Head (White with black contour & dynamic flickering!)
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

    } else {
      // Death dissolve particles
      const t = player.deathTimer;
      b.fillStyle = '#ffffff';
      for (let i = 0; i < 18; i++) {
        const a = (i / 18) * Math.PI * 2;
        const dist = t * 50 * (0.5 + (i % 3) * 0.35);
        b.fillRect(Math.cos(a) * dist, Math.sin(a) * dist + t * t * 70, 2, 2);
      }
    }

    b.restore();
  }

  // Draw Pixel HUD: Shield with Cross in Top-Left (Matches screenshot 2 & 5!)
  drawPixelHUD(b, player) {
    b.save();

    // Shield Icon (Top-Left, x: 18, y: 16)
    const sx = 18;
    const sy = 16;

    // Outer shield border
    b.fillStyle = '#000000';
    b.strokeStyle = '#ffffff';
    b.lineWidth = 1.5;
    b.beginPath();
    b.moveTo(sx, sy);
    b.lineTo(sx + 14, sy);
    b.lineTo(sx + 14, sy + 10);
    b.lineTo(sx + 7, sy + 18);
    b.lineTo(sx, sy + 10);
    b.closePath();
    b.fill();
    b.stroke();

    // White Cross inside Shield
    b.fillStyle = '#ffffff';
    b.fillRect(sx + 6, sy + 3, 2, 11);
    b.fillRect(sx + 2, sy + 6, 10, 2);

    b.restore();
  }

  // Scale buffer onto screen maintaining 1:1 square pixel aspect ratio (No distortion!)
  presentToScreen() {
    const ctx = this.ctx;
    const scrW = this.canvas.width;
    const scrH = this.canvas.height;

    // Fill screen with deep black background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, scrW, scrH);

    // Calculate maximum integer or proportional scale preserving 240x480 aspect ratio
    const scale = Math.min(scrW / this.vW, scrH / this.vH);
    const drawW = Math.round(this.vW * scale);
    const drawH = Math.round(this.vH * scale);

    const destX = Math.round((scrW - drawW) * 0.5);
    const destY = Math.round((scrH - drawH) * 0.5);

    let shakeX = 0;
    let shakeY = 0;
    if (this.shake > 0) {
      shakeX = (Math.random() * 2 - 1) * this.shake * scale;
      shakeY = (Math.random() * 2 - 1) * this.shake * scale;
    }

    ctx.drawImage(
      this.buffer,
      0, 0, this.vW, this.vH,
      destX + shakeX, destY + shakeY, drawW, drawH
    );
  }
}

window.TowerRenderer = TowerRenderer;
