// Multi-Platform Input System for Nightclimb
// Supports: Touch Swipe, Mouse Wheel (Digital Crown style), Virtual Crank, Keyboard
class InputController {
  constructor(player) {
    this.player = player;
    this.keys = {};
    this.lastTouchY = null;
    this.isDragging = false;

    // Virtual Crank State
    this.crankEl = document.getElementById('crank-container');
    this.crankArm = document.getElementById('crank-arm');
    this.crankAngle = 0; // Radians
    this.isCranking = false;
    this.crankCenter = { x: 0, y: 0 };
    this.lastCrankTickAngle = 0;

    this.initEvents();
  }

  initEvents() {
    // 1. Mouse Wheel / Trackpad (Direct Apple Watch Digital Crown feel)
    window.addEventListener('wheel', (e) => {
      // deltaY > 0 is scroll down (descend or advance based on inverted wheel)
      // Standard scroll up = climb
      const deltaMeters = -e.deltaY * 0.0035;
      this.player.addDelta(deltaMeters);
      this.updateCrankFromClimb(deltaMeters);
    }, { passive: true });

    // 2. Keyboard (W/S or Up/Down)
    window.addEventListener('keydown', (e) => {
      this.keys[e.key.toLowerCase()] = true;
      if (['arrowup', 'arrowdown', ' '].includes(e.key.toLowerCase())) {
        e.preventDefault();
      }
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.key.toLowerCase()] = false;
    });

    // 3. Screen Drag (Touch & Mouse)
    const container = document.getElementById('game-container');
    
    // Touch Events
    container.addEventListener('touchstart', (e) => {
      if (e.target.closest('#crank-container') || e.target.closest('button')) return;
      if (e.touches.length > 0) {
        this.lastTouchY = e.touches[0].clientY;
        this.isDragging = true;
      }
    }, { passive: true });

    container.addEventListener('touchmove', (e) => {
      if (!this.isDragging || e.touches.length === 0) return;
      const currentY = e.touches[0].clientY;
      const deltaY = this.lastTouchY - currentY; // Upward swipe = climb
      this.lastTouchY = currentY;

      const deltaMeters = deltaY * 0.015;
      this.player.addDelta(deltaMeters);
      this.updateCrankFromClimb(deltaMeters);
    }, { passive: true });

    window.addEventListener('touchend', () => {
      this.isDragging = false;
      this.lastTouchY = null;
    });

    // Mouse Drag
    container.addEventListener('mousedown', (e) => {
      if (e.target.closest('#crank-container') || e.target.closest('button')) return;
      this.lastTouchY = e.clientY;
      this.isDragging = true;
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      const currentY = e.clientY;
      const deltaY = this.lastTouchY - currentY;
      this.lastTouchY = currentY;

      const deltaMeters = deltaY * 0.012;
      this.player.addDelta(deltaMeters);
      this.updateCrankFromClimb(deltaMeters);
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // 4. Virtual Crank Specific Handling
    this.initVirtualCrank();
  }

  initVirtualCrank() {
    if (!this.crankEl) return;

    const startCrank = (clientX, clientY) => {
      const rect = this.crankEl.getBoundingClientRect();
      this.crankCenter = {
        x: rect.left + rect.width * 0.5,
        y: rect.top + rect.height * 0.5 - 10
      };
      this.isCranking = true;
      this.lastCrankAngle = Math.atan2(clientY - this.crankCenter.y, clientX - this.crankCenter.x);
    };

    const moveCrank = (clientX, clientY) => {
      if (!this.isCranking) return;
      const newAngle = Math.atan2(clientY - this.crankCenter.y, clientX - this.crankCenter.x);
      let deltaAngle = newAngle - this.lastCrankAngle;

      // Handle wrapping across PI / -PI boundary
      if (deltaAngle > Math.PI) deltaAngle -= Math.PI * 2;
      if (deltaAngle < -Math.PI) deltaAngle += Math.PI * 2;

      this.lastCrankAngle = newAngle;
      this.crankAngle += deltaAngle;

      // Clockwise rotation = climb upward
      const deltaMeters = deltaAngle * 0.35;
      this.player.addDelta(deltaMeters);

      // Render rotated crank arm
      if (this.crankArm) {
        this.crankArm.style.transform = `rotate(${this.crankAngle}rad)`;
      }

      // Play crank ratchet tick
      if (Math.abs(this.crankAngle - this.lastCrankTickAngle) > 0.35) {
        window.soundEngine?.playCrankTick(Math.sign(deltaAngle));
        this.lastCrankTickAngle = this.crankAngle;
      }
    };

    const stopCrank = () => {
      this.isCranking = false;
    };

    // Crank Mouse Events
    this.crankEl.addEventListener('mousedown', (e) => {
      e.stopPropagation();
      startCrank(e.clientX, e.clientY);
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isCranking) {
        e.preventDefault();
        moveCrank(e.clientX, e.clientY);
      }
    });

    window.addEventListener('mouseup', stopCrank);

    // Crank Touch Events
    this.crankEl.addEventListener('touchstart', (e) => {
      e.stopPropagation();
      if (e.touches.length > 0) {
        startCrank(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: false });

    window.addEventListener('touchmove', (e) => {
      if (this.isCranking && e.touches.length > 0) {
        e.preventDefault();
        moveCrank(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: false });

    window.addEventListener('touchend', stopCrank);
  }

  updateCrankFromClimb(deltaMeters) {
    if (this.isCranking) return; // Don't fight user's finger on crank
    const deltaAngle = deltaMeters * 2.8;
    this.crankAngle += deltaAngle;
    if (this.crankArm) {
      this.crankArm.style.transform = `rotate(${this.crankAngle}rad)`;
    }
    if (Math.abs(this.crankAngle - this.lastCrankTickAngle) > 0.45) {
      window.soundEngine?.playCrankTick(Math.sign(deltaMeters));
      this.lastCrankTickAngle = this.crankAngle;
    }
  }

  update(dt) {
    // Process keyboard continuous input
    let keyDelta = 0;
    if (this.keys['arrowup'] || this.keys['w']) {
      keyDelta += 3.8 * dt;
    }
    if (this.keys['arrowdown'] || this.keys['s']) {
      keyDelta -= 3.8 * dt;
    }

    if (keyDelta !== 0) {
      this.player.addDelta(keyDelta);
      this.updateCrankFromClimb(keyDelta);
    }
  }
}

window.InputController = InputController;

