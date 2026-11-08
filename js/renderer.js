// 1-Bit / Dithered Gothic Tower Spiral Renderer
class TowerRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = window.innerWidth;
    this.height = window.innerHeight;

    this.towerRadius = 140; // Pixels
    this.ledgeWidth = 45;
    this.pitch = 70; // Vertical pixels per meter
    this.spiralRate = (Math.PI * 2) / 9.0; // 1 full revolution every 9 meters

    this.particles = [];
    this.bats = [];
    this.screenShake = 0;

    this.initBackgroundElements();
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);

    // Dynamic tower radius based on screen size
    this.towerRadius = Math.min(this.width * 0.28, 160);
    this.ledgeWidth = Math.min(this.towerRadius * 0.35, 45);
  }

  initBackgroundElements() {
    // Ambient floating embers & dust
    for (let i = 0; i < 35; i++) {
      this.particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vy: -0.3 - Math.random() * 0.6,
        size: Math.random() < 0.8 ? 1.5 : 2.5,
        alpha: 0.3 + Math.random() * 0.5
      });
    }

    // Occasional silhouetted bats
    for (let i = 0; i < 4; i++) {
      this.bats.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * (window.innerHeight * 0.6),
        vx: 1.2 + Math.random() * 1.5,
        vy: (Math.random() - 0.5) * 0.8,
        wing: Math.random() * 10
      });
    }
  }

  addShake(amount) {
    this.screenShake = Math.max(this.screenShake, amount);
  }

  render(player, obstacleManager, dt) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    // Screen shake decay
    let offsetX = 0;
    let offsetY = 0;
    if (this.screenShake > 0) {
      offsetX = (Math.random() * 2 - 1) * this.screenShake;
      offsetY = (Math.random() * 2 - 1) * this.screenShake;
      this.screenShake = Math.max(0, this.screenShake - dt * 15);
    }

    ctx.save();
    ctx.translate(offsetX, offsetY);

    // 1. Clear background (Night sky)
    ctx.fillStyle = '#090a0d';
    ctx.fillRect(0, 0, w, h);

    // 2. Distant Moon & Stars
    this.drawBackground(ctx, w, h, player.altitude);

    // Center of tower on screen
    const centerX = w * 0.5;
    // Keep player framed in lower-middle half of screen
    const centerY = h * 0.62;
    const camAlt = player.altitude;

    // 3. Render back-half of spiral (behind tower)
    this.renderSpiralStairs(ctx, centerX, centerY, camAlt, false);

    // 4. Render main cylindrical Tower body
    this.renderTowerCylinder(ctx, centerX, centerY, camAlt, w, h);

    // 5. Render front-half of spiral (in front of tower)
    this.renderSpiralStairs(ctx, centerX, centerY, camAlt, true);

    // 6. Render Traps & Obstacles
    this.renderObstacles(ctx, obstacleManager.obstacles, centerX, centerY, camAlt);

    // 7. Render Player (Roland)
    this.renderPlayer(ctx, player, centerX, centerY, camAlt);

    // 8. Foreground fog & ambient particles
    this.renderAtmosphere(ctx, w, h, dt);

    ctx.restore();
  }

  drawBackground(ctx, w, h, altitude) {
    // Distant gothic crescent moon
    const moonX = w * 0.22;
    const moonY = h * 0.18 + (altitude * 0.2) % 30; // Parallax slow drift
    ctx.save();
    ctx.fillStyle = '#e8e5db';
    ctx.beginPath();
    ctx.arc(moonX, moonY, 32, 0, Math.PI * 2);
    ctx.fill();

    // Dark bite for crescent
    ctx.fillStyle = '#090a0d';
    ctx.beginPath();
    ctx.arc(moonX + 12, moonY - 4, 28, 0, Math.PI * 2);
    ctx.fill();

    // Distant mountain silhouettes
    ctx.fillStyle = '#12141a';
    ctx.beginPath();
    ctx.moveTo(0, h * 0.85);
    ctx.lineTo(w * 0.25, h * 0.72);
    ctx.lineTo(w * 0.5, h * 0.82);
    ctx.lineTo(w * 0.8, h * 0.68);
    ctx.lineTo(w, h * 0.80);
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // Cylindrical 1D-to-3D projection
  projectPoint(altitude, camAlt, centerX, centerY, radialOffset = 0) {
    const deltaAlt = altitude - camAlt;
    const screenY = centerY - deltaAlt * this.pitch;

    const angle = altitude * this.spiralRate;
    const r = this.towerRadius + radialOffset;

    const normX = Math.sin(angle);
    const normZ = Math.cos(angle); // +1 is closest to camera, -1 is behind tower

    const screenX = centerX + normX * r;

    return {
      x: screenX,
      y: screenY,
      z: normZ,
      angle: angle,
      isFront: normZ >= -0.15
    };
  }

  renderTowerCylinder(ctx, centerX, centerY, camAlt, w, h) {
    ctx.save();

    const tRadius = this.towerRadius;
    const leftX = centerX - tRadius;
    const rightX = centerX + tRadius;

    // Tower base vertical fill
    const grad = ctx.createLinearGradient(leftX, 0, rightX, 0);
    grad.addColorStop(0.0, '#101217');
    grad.addColorStop(0.2, '#20242d');
    grad.addColorStop(0.5, '#323846');
    grad.addColorStop(0.8, '#1e222a');
    grad.addColorStop(1.0, '#0c0e12');

    ctx.fillStyle = grad;
    ctx.fillRect(leftX, 0, tRadius * 2, h);

    // Tower border lines (solid gothic masonry edges)
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(leftX, 0);
    ctx.lineTo(leftX, h);
    ctx.moveTo(rightX, 0);
    ctx.lineTo(rightX, h);
    ctx.stroke();

    // Dithered horizontal stone brick courses with vertical parallax
    ctx.strokeStyle = 'rgba(243, 239, 230, 0.08)';
    ctx.lineWidth = 1;
    const brickHeight = 24;
    const scrollOffset = (camAlt * this.pitch) % brickHeight;

    for (let y = -brickHeight; y < h + brickHeight; y += brickHeight) {
      const lineY = y + scrollOffset;
      ctx.beginPath();
      ctx.moveTo(leftX + 4, lineY);
      ctx.lineTo(rightX - 4, lineY);
      ctx.stroke();

      // Masonry vertical notches
      const rowIdx = Math.floor((camAlt * this.pitch + y) / brickHeight);
      const shift = (rowIdx % 2) * 20;
      for (let bx = leftX + 16 + shift; bx < rightX - 10; bx += 40) {
        ctx.beginPath();
        ctx.moveTo(bx, lineY);
        ctx.lineTo(bx, lineY + brickHeight);
        ctx.stroke();
      }
    }

    // Occasional gothic narrow arch windows on the tower
    const windowInterval = 6.0; // Every 6 meters
    const baseWinAlt = Math.floor((camAlt - 8) / windowInterval) * windowInterval;
    for (let alt = baseWinAlt; alt < camAlt + 16; alt += windowInterval) {
      const p = this.projectPoint(alt, camAlt, centerX, centerY, 0);
      if (p.isFront && p.z > 0.4) {
        ctx.fillStyle = '#060709';
        ctx.strokeStyle = 'rgba(243, 239, 230, 0.25)';
        ctx.lineWidth = 1.5;

        const winW = 12 * p.z;
        const winH = 28 * p.z;
        ctx.beginPath();
        ctx.roundRect(p.x - winW * 0.5, p.y - winH * 0.5, winW, winH, [winW * 0.5, winW * 0.5, 0, 0]);
        ctx.fill();
        ctx.stroke();
      }
    }

    ctx.restore();
  }

  renderSpiralStairs(ctx, centerX, centerY, camAlt, renderFront) {
    ctx.save();

    // Render a span of stairs around camera altitude
    const stepCount = 90;
    const stepDelta = 0.25; // meter per step
    const startAlt = Math.floor((camAlt - 7) / stepDelta) * stepDelta;

    for (let i = 0; i < stepCount; i++) {
      const alt = startAlt + i * stepDelta;
      const inner = this.projectPoint(alt, camAlt, centerX, centerY, 0);
      const outer = this.projectPoint(alt, camAlt, centerX, centerY, this.ledgeWidth);

      // Check whether this step is in front or behind the cylinder
      const isStepFront = (inner.z + outer.z) * 0.5 >= -0.05;

      if (isStepFront !== renderFront) continue;

      // Draw the step ledge
      const stepThick = 7;
      const lightFactor = Math.max(0.15, (inner.z + 1.0) * 0.5);

      // Step surface
      ctx.fillStyle = renderFront 
        ? `rgb(${Math.floor(210 * lightFactor)}, ${Math.floor(205 * lightFactor)}, ${Math.floor(195 * lightFactor)})`
        : '#15171e';
      ctx.strokeStyle = '#0a0b0e';
      ctx.lineWidth = 1.5;

      ctx.beginPath();
      ctx.moveTo(inner.x, inner.y);
      ctx.lineTo(outer.x, outer.y);
      ctx.lineTo(outer.x, outer.y + stepThick);
      ctx.lineTo(inner.x, inner.y + stepThick);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }

  renderObstacles(ctx, obstacles, centerX, centerY, camAlt) {
    for (const obs of obstacles) {
      const p = this.projectPoint(obs.altitude, camAlt, centerX, centerY, this.ledgeWidth * 0.5);

      // Only draw when roughly in view
      if (p.y < -50 || p.y > this.height + 50) continue;

      ctx.save();
      ctx.translate(p.x, p.y);

      if (obs.type === 'SPIKE') {
        // Base plate
        ctx.fillStyle = '#1c1f26';
        ctx.strokeStyle = '#f3efe6';
        ctx.lineWidth = 1;
        ctx.fillRect(-14, -2, 28, 4);
        ctx.strokeRect(-14, -2, 28, 4);

        // Extended or shaking spikes
        if (obs.spikeHeight > 0.05) {
          const maxH = 22;
          const curH = maxH * obs.spikeHeight;

          ctx.fillStyle = '#f3efe6';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1.5;

          // 3 sharp spikes
          [-8, 0, 8].forEach(sx => {
            ctx.beginPath();
            ctx.moveTo(sx - 3, -2);
            ctx.lineTo(sx, -2 - curH);
            ctx.lineTo(sx + 3, -2);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
          });
        }
      } else if (obs.type === 'PENDULUM') {
        const armLength = 80;
        const currentAngle = obs.angle * 0.85; // Swing arc

        ctx.rotate(currentAngle);
        // Chain / rod
        ctx.strokeStyle = '#b8bfc9';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, -armLength);
        ctx.lineTo(0, 0);
        ctx.stroke();

        // Massive Crescent Scythe Blade
        ctx.fillStyle = '#f3efe6';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, 0, 22, -Math.PI * 0.4, Math.PI * 0.4);
        ctx.arc(10, 0, 18, Math.PI * 0.35, -Math.PI * 0.35, true);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (obs.type === 'CRUMBLE') {
        if (!obs.isCollapsed) {
          ctx.translate(obs.shakeOffset, 0);
          // Cracked stone plate
          ctx.fillStyle = '#4a5260';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 2;
          ctx.fillRect(-16, -3, 32, 6);
          ctx.strokeRect(-16, -3, 32, 6);

          if (obs.isTriggered) {
            // Draw fracture cracks
            ctx.strokeStyle = '#f3efe6';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(-10, -2);
            ctx.lineTo(-2, 2);
            ctx.lineTo(8, -1);
            ctx.stroke();
          }
        } else {
          // Hollow missing gap marker
          ctx.fillStyle = 'rgba(201, 74, 74, 0.4)';
          ctx.fillRect(-14, -2, 28, 4);
        }
      } else if (obs.type === 'GARGOYLE') {
        // Gargoyle head on inner wall
        ctx.fillStyle = '#22262e';
        ctx.strokeStyle = '#f3efe6';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(-20, -10, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Fire / smoke burst across path
        if (obs.isBlasting) {
          ctx.fillStyle = Math.random() < 0.5 ? '#f3efe6' : '#cbb279';
          for (let f = 0; f < 5; f++) {
            const fx = -12 + Math.random() * 24;
            const fy = -14 + Math.random() * 8;
            ctx.beginPath();
            ctx.arc(fx, fy, 4 + Math.random() * 5, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }

      ctx.restore();
    }
  }

  renderPlayer(ctx, player, centerX, centerY, camAlt) {
    const p = this.projectPoint(player.altitude, camAlt, centerX, centerY, this.ledgeWidth * 0.5);

    ctx.save();
    ctx.translate(p.x, p.y);

    if (player.isAlive) {
      // Facing direction scale
      const dirScale = player.direction;
      ctx.scale(dirScale, 1);

      // Character Shadow on stone step
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.beginPath();
      ctx.ellipse(0, 0, 10, 4, 0, 0, Math.PI * 2);
      ctx.fill();

      // Roland / Wanderer Silhouette:
      const legBob = Math.sin(player.walkCycle * Math.PI * 0.5) * 3;

      // Legs / Boots
      ctx.fillStyle = '#101217';
      ctx.fillRect(-4, -10, 3, 10 - legBob);
      ctx.fillRect(1, -10, 3, 10 + legBob);

      // Tunic / Torso
      ctx.fillStyle = '#2b313d';
      ctx.strokeStyle = '#f3efe6';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.rect(-5, -24, 10, 14);
      ctx.fill();
      ctx.stroke();

      // Flowing Gothic Cloak
      ctx.fillStyle = '#f3efe6';
      ctx.beginPath();
      ctx.moveTo(-5, -24);
      ctx.lineTo(-12 - Math.abs(player.velocity) * 0.4, -14);
      ctx.lineTo(-6, -6);
      ctx.closePath();
      ctx.fill();

      // Head / Hood
      ctx.fillStyle = '#060708';
      ctx.strokeStyle = '#f3efe6';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(0, -29, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Glowing monocle/eye slit
      ctx.fillStyle = '#cbb279';
      ctx.fillRect(2, -30, 2, 2);

    } else {
      // Death dissolve / shatter animation
      const t = player.deathTimer;
      ctx.fillStyle = '#f3efe6';
      for (let i = 0; i < 16; i++) {
        const angle = (i / 16) * Math.PI * 2;
        const dist = t * 65 * (0.6 + (i % 3) * 0.3);
        const px = Math.cos(angle) * dist;
        const py = Math.sin(angle) * dist + (t * t * 90); // gravity
        ctx.fillRect(px, py, 3, 3);
      }
    }

    ctx.restore();
  }

  renderAtmosphere(ctx, w, h, dt) {
    // Floating particles (dust & embers)
    ctx.fillStyle = '#f3efe6';
    for (const p of this.particles) {
      p.y += p.vy;
      if (p.y < 0) {
        p.y = h;
        p.x = Math.random() * w;
      }
      ctx.globalAlpha = p.alpha;
      ctx.fillRect(p.x, p.y, p.size, p.size);
    }

    // Flying bats
    ctx.globalAlpha = 0.75;
    ctx.fillStyle = '#0a0c10';
    for (const b of this.bats) {
      b.x += b.vx;
      b.y += b.vy;
      b.wing += 0.2;
      if (b.x > w + 20) {
        b.x = -20;
        b.y = Math.random() * (h * 0.5);
      }

      ctx.save();
      ctx.translate(b.x, b.y);
      const wingSpan = Math.sin(b.wing) * 6;
      ctx.beginPath();
      ctx.moveTo(-6, wingSpan);
      ctx.lineTo(0, -2);
      ctx.lineTo(6, wingSpan);
      ctx.lineTo(0, 2);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    ctx.globalAlpha = 1.0;
  }
}

window.TowerRenderer = TowerRenderer;

