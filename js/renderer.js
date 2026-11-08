// Authentic 1-Bit Monochrome Bayer-Dithered Renderer for Nightclimb
// Matches the visual style of "A Fool's Errand" & "Return of the Obra Dinn"

class TowerRenderer {
  constructor(mainCanvas) {
    this.mainCanvas = mainCanvas;
    this.mainCtx = mainCanvas.getContext('2d');

    // Low-resolution 1-bit buffer (Crisp chunky pixels)
    this.bufferW = 240;
    this.bufferH = 420;
    this.offscreen = document.createElement('canvas');
    this.offscreen.width = this.bufferW;
    this.offscreen.height = this.bufferH;
    this.ctx = this.offscreen.getContext('2d', { willReadFrequently: true });

    // 4x4 Bayer Dither Matrix normalized to 0..255
    this.bayer4x4 = [
      [  0, 128,  32, 160 ],
      [ 192,  64, 224,  96 ],
      [  48, 176,  16, 144 ],
      [ 240, 112, 208,  80 ]
    ];

    // Cylinder & Staircase settings
    this.towerRadius = 52;
    this.ledgeWidth = 26;
    this.pitch = 30; // vertical pixels per meter
    this.spiralRate = (Math.PI * 2) / 8.0; // 1 full revolution every 8 meters

    this.torchFlicker = 0;
    this.time = 0;

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.mainCanvas.width = w;
    this.mainCanvas.height = h;
    this.mainCtx.imageSmoothingEnabled = false;
  }

  // Cylindrical projection from 1D altitude into 2.5D coordinates
  project(alt, camAlt, centerX, centerY, radialOffset = 0) {
    const dy = (alt - camAlt) * this.pitch;
    const screenY = centerY - dy;

    const angle = alt * this.spiralRate;
    const r = this.towerRadius + radialOffset;

    const sinA = Math.sin(angle);
    const cosA = Math.cos(angle); // +1 = front, -1 = back

    const screenX = centerX + sinA * r;

    return {
      x: Math.round(screenX),
      y: Math.round(screenY),
      z: cosA,
      angle: angle,
      isFront: cosA >= -0.15
    };
  }

  render(player, obstacleManager, dt) {
    this.time += dt;
    this.torchFlicker = Math.sin(this.time * 18) * 3 + Math.cos(this.time * 29) * 2;

    const ctx = this.ctx;
    const w = this.bufferW;
    const h = this.bufferH;

    // 1. Clear with deep black
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, w, h);

    const centerX = Math.round(w * 0.52);
    const centerY = Math.round(h * 0.58);
    const camAlt = player.altitude;

    // 2. Distant Arch Window with Glowing Moon (Upper Left, like screenshot)
    this.drawMoonWindow(ctx, w, h, camAlt);

    // 3. Render back-half of stairs (behind tower)
    this.renderStairs(ctx, centerX, centerY, camAlt, false);

    // 4. Render central Tower Cylinder & Wall Bricks
    this.renderTowerCylinder(ctx, centerX, centerY, camAlt, w, h);

    // 5. Render wall-mounted torches
    this.renderWallTorches(ctx, centerX, centerY, camAlt);

    // 6. Render front-half of stairs
    this.renderStairs(ctx, centerX, centerY, camAlt, true);

    // 7. Render Traps
    this.renderTraps(ctx, obstacleManager.obstacles, centerX, centerY, camAlt);

    // 8. Render Roland (The Torchbearer)
    const rolandPos = this.project(player.altitude, camAlt, centerX, centerY, this.ledgeWidth * 0.5);
    this.renderRoland(ctx, player, rolandPos);

    // 9. Apply Dynamic Torchlight Radiance Map
    this.applyTorchLightCone(ctx, rolandPos, centerX, centerY, camAlt);

    // 10. Perform 1-BIT BAYER DITHER QUANTIZATION PASS
    this.apply1BitDither(ctx, w, h);

    // 11. Scale up onto main screen canvas with crisp pixel edges
    this.mainCtx.drawImage(
      this.offscreen,
      0, 0, w, h,
      0, 0, this.mainCanvas.width, this.mainCanvas.height
    );
  }

  drawMoonWindow(ctx, w, h, camAlt) {
    // Fixed window position in upper left sky
    const winX = 38;
    const winY = 65 + (camAlt * 0.5) % 180; // Slow parallax shift
    if (winY > h + 50) return;

    ctx.save();
    // Arched window outline
    ctx.fillStyle = '#222222';
    ctx.beginPath();
    ctx.arc(winX, winY - 14, 14, Math.PI, 0);
    ctx.lineTo(winX + 14, winY + 18);
    ctx.lineTo(winX - 14, winY + 18);
    ctx.closePath();
    ctx.fill();

    // Glowing bright white crescent moon inside window
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(winX - 1, winY - 3, 10, 0, Math.PI * 2);
    ctx.fill();

    // Moon shadow bite
    ctx.fillStyle = '#222222';
    ctx.beginPath();
    ctx.arc(winX + 3, winY - 5, 9, 0, Math.PI * 2);
    ctx.fill();

    // Soft stipple moonlight halo around window
    const moonGrad = ctx.createRadialGradient(winX, winY - 4, 10, winX, winY - 4, 38);
    moonGrad.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
    moonGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = moonGrad;
    ctx.beginPath();
    ctx.arc(winX, winY - 4, 38, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  renderTowerCylinder(ctx, centerX, centerY, camAlt, w, h) {
    ctx.save();
    const r = this.towerRadius;
    const leftX = centerX - r;
    const rightX = centerX + r;

    // Cylinder base shading (Grayscale for dither pass)
    const grad = ctx.createLinearGradient(leftX, 0, rightX, 0);
    grad.addColorStop(0.0, '#101010');
    grad.addColorStop(0.2, '#353535');
    grad.addColorStop(0.5, '#555555');
    grad.addColorStop(0.8, '#303030');
    grad.addColorStop(1.0, '#0a0a0a');

    ctx.fillStyle = grad;
    ctx.fillRect(leftX, 0, r * 2, h);

    // Stone masonry courses with dithered stone texture
    ctx.strokeStyle = '#050505';
    ctx.lineWidth = 1;
    const rowH = 12;
    const scroll = (camAlt * this.pitch) % rowH;

    for (let y = -rowH; y < h + rowH; y += rowH) {
      const lineY = Math.round(y + scroll);
      ctx.beginPath();
      ctx.moveTo(leftX, lineY);
      ctx.lineTo(rightX, lineY);
      ctx.stroke();

      // Vertical block joints
      const rowIdx = Math.floor((camAlt * this.pitch + y) / rowH);
      const shift = (rowIdx % 2) * 12;
      for (let bx = leftX + 8 + shift; bx < rightX - 4; bx += 20) {
        ctx.beginPath();
        ctx.moveTo(bx, lineY);
        ctx.lineTo(bx, lineY + rowH);
        ctx.stroke();
      }
    }

    ctx.restore();
  }

  renderStairs(ctx, centerX, centerY, camAlt, renderFront) {
    ctx.save();
    const stepDelta = 0.28; // meter per step
    const stepCount = 50;
    const startAlt = Math.floor((camAlt - 5) / stepDelta) * stepDelta;

    for (let i = 0; i < stepCount; i++) {
      const alt = startAlt + i * stepDelta;
      const inner = this.project(alt, camAlt, centerX, centerY, 0);
      const outer = this.project(alt, camAlt, centerX, centerY, this.ledgeWidth);

      const isStepFront = (inner.z + outer.z) * 0.5 >= -0.05;
      if (isStepFront !== renderFront) continue;

      const light = Math.max(0.25, (inner.z + 1.0) * 0.45);
      const shade = Math.floor(light * 200);

      ctx.fillStyle = renderFront ? `rgb(${shade}, ${shade}, ${shade})` : '#181818';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;

      // Draw thick stone step block
      const stepThick = 5;
      ctx.beginPath();
      ctx.moveTo(inner.x, inner.y);
      ctx.lineTo(outer.x, outer.y);
      ctx.lineTo(outer.x, outer.y + stepThick);
      ctx.lineTo(inner.x, inner.y + stepThick);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Top step highlight
      if (renderFront) {
        ctx.strokeStyle = `rgb(${shade + 40}, ${shade + 40}, ${shade + 40})`;
        ctx.beginPath();
        ctx.moveTo(inner.x, inner.y);
        ctx.lineTo(outer.x, outer.y);
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  renderWallTorches(ctx, centerX, centerY, camAlt) {
    const torchInterval = 7.0; // Every 7 meters on tower wall
    const baseAlt = Math.floor((camAlt - 7) / torchInterval) * torchInterval;

    for (let alt = baseAlt; alt < camAlt + 12; alt += torchInterval) {
      const p = this.project(alt, camAlt, centerX, centerY, 2);
      if (p.isFront && p.z > 0.25) {
        ctx.save();
        ctx.translate(p.x, p.y - 14);

        // Torch iron wall sconce
        ctx.fillStyle = '#050505';
        ctx.fillRect(-2, -4, 4, 10);

        // Torch Flame
        const flameH = 6 + Math.random() * 3;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(-3, -4);
        ctx.lineTo(0, -4 - flameH);
        ctx.lineTo(3, -4);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
      }
    }
  }

  renderTraps(ctx, obstacles, centerX, centerY, camAlt) {
    for (const obs of obstacles) {
      const p = this.project(obs.altitude, camAlt, centerX, centerY, this.ledgeWidth * 0.5);
      if (p.y < -30 || p.y > this.bufferH + 30) continue;

      ctx.save();
      ctx.translate(p.x, p.y);

      if (obs.type === 'SPIKE') {
        // Base plate with dark holes
        ctx.fillStyle = '#101010';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.fillRect(-10, -1, 20, 3);
        ctx.strokeRect(-10, -1, 20, 3);

        if (obs.spikeHeight > 0.05) {
          const maxH = 14;
          const h = maxH * obs.spikeHeight;
          ctx.fillStyle = '#ffffff';
          [-6, 0, 6].forEach(sx => {
            ctx.beginPath();
            ctx.moveTo(sx - 2, -1);
            ctx.lineTo(sx, -1 - h);
            ctx.lineTo(sx + 2, -1);
            ctx.closePath();
            ctx.fill();
          });
        }
      } else if (obs.type === 'PENDULUM') {
        const armL = 50;
        ctx.rotate(obs.angle * 0.85);

        ctx.strokeStyle = '#aaaaaa';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, -armL);
        ctx.lineTo(0, 0);
        ctx.stroke();

        // Curved Scythe Blade
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(0, 0, 14, -Math.PI * 0.4, Math.PI * 0.4);
        ctx.arc(6, 0, 11, Math.PI * 0.35, -Math.PI * 0.35, true);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (obs.type === 'CRUMBLE') {
        if (!obs.isCollapsed) {
          ctx.translate(obs.shakeOffset * 0.5, 0);
          ctx.fillStyle = '#444444';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1;
          ctx.fillRect(-10, -2, 20, 4);
          ctx.strokeRect(-10, -2, 20, 4);
        } else {
          ctx.fillStyle = '#000000';
          ctx.fillRect(-8, -2, 16, 4);
        }
      }

      ctx.restore();
    }
  }

  renderRoland(ctx, player, rolandPos) {
    ctx.save();
    ctx.translate(rolandPos.x, rolandPos.y);

    if (player.isAlive) {
      ctx.scale(player.direction, 1);

      // Footstep bob
      const bob = Math.sin(player.walkCycle * Math.PI * 0.5) * 2;

      // Legs / Dark Boots
      ctx.fillStyle = '#050505';
      ctx.fillRect(-3, -7, 2, 7 - bob);
      ctx.fillRect(1, -7, 2, 7 + bob);

      // Bright White Tunic / Body (Exact match to screenshot!)
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(-4, -18, 8, 11, [2, 2, 0, 0]);
      ctx.fill();
      ctx.stroke();

      // Cape fluttering back
      ctx.fillStyle = '#222222';
      ctx.beginPath();
      ctx.moveTo(-4, -18);
      ctx.lineTo(-8 - Math.abs(player.velocity) * 0.2, -12);
      ctx.lineTo(-4, -8);
      ctx.closePath();
      ctx.fill();

      // Squire Cap / Hood
      ctx.fillStyle = '#111111';
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(0, -21, 4.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Roland holding Burning Torch in front hand!
      const torchX = 5;
      const torchY = -16;
      ctx.fillStyle = '#000000';
      ctx.fillRect(torchX, torchY, 2, 8); // torch stick

      // Burning flame head
      const flameH = 6 + Math.random() * 3;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(torchX - 1, torchY);
      ctx.lineTo(torchX + 1, torchY - flameH);
      ctx.lineTo(torchX + 3, torchY);
      ctx.closePath();
      ctx.fill();

    } else {
      // Death dissolve particles
      const t = player.deathTimer;
      ctx.fillStyle = '#ffffff';
      for (let i = 0; i < 14; i++) {
        const ang = (i / 14) * Math.PI * 2;
        const d = t * 45 * (0.5 + (i % 3) * 0.4);
        ctx.fillRect(Math.cos(ang) * d, Math.sin(ang) * d + t * t * 60, 2, 2);
      }
    }

    ctx.restore();
  }

  // Radial dithered light cone emitted from Roland's torch
  applyTorchLightCone(ctx, rolandPos, centerX, centerY, camAlt) {
    if (!rolandPos) return;

    ctx.save();
    // Torch position in buffer coordinates
    const tx = rolandPos.x + 5;
    const ty = rolandPos.y - 18;
    const radius = 68 + this.torchFlicker;

    // Torch radial light gradient
    const grad = ctx.createRadialGradient(tx, ty, 6, tx, ty, radius);
    grad.addColorStop(0.0, 'rgba(255, 255, 255, 0.95)');
    grad.addColorStop(0.3, 'rgba(210, 210, 210, 0.7)');
    grad.addColorStop(0.65, 'rgba(120, 120, 120, 0.35)');
    grad.addColorStop(1.0, 'rgba(0, 0, 0, 0.0)');

    ctx.globalCompositeOperation = 'screen';
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(tx, ty, radius, 0, Math.PI * 2);
    ctx.fill();

    // Wall torches radiance
    const torchInterval = 7.0;
    const baseAlt = Math.floor((camAlt - 7) / torchInterval) * torchInterval;
    for (let alt = baseAlt; alt < camAlt + 12; alt += torchInterval) {
      const p = this.project(alt, camAlt, centerX, centerY, 2);
      if (p.isFront && p.z > 0.25) {
        const wGrad = ctx.createRadialGradient(p.x, p.y - 18, 4, p.x, p.y - 18, 42);
        wGrad.addColorStop(0.0, 'rgba(255, 255, 255, 0.7)');
        wGrad.addColorStop(1.0, 'rgba(0, 0, 0, 0.0)');
        ctx.fillStyle = wGrad;
        ctx.beginPath();
        ctx.arc(p.x, p.y - 18, 42, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    ctx.restore();
  }

  // 1-Bit Bayer Matrix Quantization (Converts entire screen to true black and white)
  apply1BitDither(ctx, w, h) {
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;
    const bayer = this.bayer4x4;

    for (let y = 0; y < h; y++) {
      const rowOffset = y * w * 4;
      const bayerRow = bayer[y % 4];

      for (let x = 0; x < w; x++) {
        const idx = rowOffset + (x * 4);

        // Perceptual grayscale luminance
        const r = data[idx];
        const g = data[idx + 1];
        const b = data[idx + 2];
        const gray = 0.299 * r + 0.587 * g + 0.114 * b;

        const threshold = bayerRow[x % 4];

        // 1-bit quantization: strictly #ffffff (255) or #000000 (0)
        const val = gray >= threshold ? 255 : 0;
        data[idx] = val;
        data[idx + 1] = val;
        data[idx + 2] = val;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imgData, 0, 0);
  }
}

window.TowerRenderer = TowerRenderer;
