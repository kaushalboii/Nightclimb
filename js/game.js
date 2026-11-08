// Nightclimb Master Game Loop & State Controller
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.renderer = new window.TowerRenderer(this.canvas);
    this.player = window.player;
    this.obstacleManager = window.obstacleManager;
    this.loreManager = window.loreManager;
    this.input = new window.InputController(this.player);

    this.state = 'TITLE'; // 'TITLE', 'PLAYING', 'GAMEOVER'
    this.lastTime = performance.now();

    // DOM UI Elements
    this.titleScreen = document.getElementById('title-screen');
    this.gameoverScreen = document.getElementById('gameover-screen');
    this.startBtn = document.getElementById('start-btn');
    this.retryBtn = document.getElementById('retry-btn');
    this.altitudeVal = document.getElementById('altitude-val');
    this.recordVal = document.getElementById('record-val');
    this.finalAlt = document.getElementById('final-alt');
    this.bestAlt = document.getElementById('best-alt');
    this.deathCause = document.getElementById('death-cause');
    this.trapsDodged = document.getElementById('traps-dodged');
    this.loreCount = document.getElementById('lore-count');

    // Persistence
    this.bestRecord = parseFloat(localStorage.getItem('nightclimb_best') || '0');
    this.updateRecordDisplay();

    this.initListeners();
    requestAnimationFrame((t) => this.loop(t));
  }

  initListeners() {
    this.startBtn.addEventListener('click', () => {
      window.soundEngine?.ensureContext();
      this.startGame();
    });

    this.retryBtn.addEventListener('click', () => {
      this.startGame();
    });

    // Also support spacebar to start/retry
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        if (this.state === 'TITLE' || this.state === 'GAMEOVER') {
          window.soundEngine?.ensureContext();
          this.startGame();
        }
      }
    });
  }

  startGame() {
    this.state = 'PLAYING';
    this.player.reset();
    this.obstacleManager.reset();

    this.titleScreen.classList.remove('active');
    this.titleScreen.classList.add('hidden');
    this.gameoverScreen.classList.remove('active');
    this.gameoverScreen.classList.add('hidden');
  }

  gameOver(cause) {
    this.state = 'GAMEOVER';
    this.player.die(cause);
    this.renderer.addShake(15);

    const score = Math.floor(this.player.highestAltitude);
    if (score > this.bestRecord) {
      this.bestRecord = score;
      localStorage.setItem('nightclimb_best', this.bestRecord.toString());
    }

    setTimeout(() => {
      this.finalAlt.textContent = `${score}m`;
      this.bestAlt.textContent = `${this.bestRecord}m`;
      this.deathCause.textContent = cause;
      this.trapsDodged.textContent = this.obstacleManager.dodgedCount.toString();
      this.loreCount.textContent = `${this.loreManager.getUnlockedCount()} / ${this.loreManager.getTotalCount()}`;

      this.gameoverScreen.classList.remove('hidden');
      this.gameoverScreen.classList.add('active');
      this.updateRecordDisplay();
    }, 1100);
  }

  updateRecordDisplay() {
    if (this.recordVal) {
      this.recordVal.innerHTML = `${Math.floor(this.bestRecord)}<span class="unit">m</span>`;
    }
  }

  loop(currentTime) {
    const dt = Math.min((currentTime - this.lastTime) / 1000, 0.1);
    this.lastTime = currentTime;

    // Process continuous keyboard movement
    this.input.update(dt);

    if (this.state === 'PLAYING') {
      this.player.update(dt);
      this.obstacleManager.update(dt, this.player.altitude);

      // Check Lore milestone unlocks
      this.loreManager.checkMilestone(this.player.altitude);

      // Check trap collision
      const collision = this.obstacleManager.checkCollision(this.player);
      if (collision.isHit) {
        this.gameOver(collision.cause);
      }

      // Update Altitude in HUD
      const curAlt = Math.max(0, Math.floor(this.player.altitude));
      this.altitudeVal.innerHTML = `${curAlt}<span class="unit">m</span>`;

      if (curAlt > this.bestRecord) {
        this.bestRecord = curAlt;
        this.updateRecordDisplay();
      }
    } else if (this.state === 'GAMEOVER') {
      this.player.update(dt);
    }

    // Render Scene
    this.renderer.render(this.player, this.obstacleManager, dt);

    requestAnimationFrame((t) => this.loop(t));
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.game = new Game();
});

