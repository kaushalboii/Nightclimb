// Master Game Controller for Nightclimb
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.renderer = new window.TowerRenderer(this.canvas);
    this.player = window.player;
    this.obstacleManager = window.obstacleManager;
    this.loreManager = window.loreManager;
    this.input = new window.InputController(this.player);

    this.state = 'TITLE'; // 'TITLE', 'PLAYING', 'GAMEOVER', 'SCROLL'
    this.lastTime = performance.now();

    // DOM Elements
    this.titleScreen = document.getElementById('title-screen');
    this.gameoverScreen = document.getElementById('gameover-screen');
    this.scrollModal = document.getElementById('scroll-modal');
    this.startBtn = document.getElementById('start-btn');
    this.retryBtn = document.getElementById('retry-btn');
    this.scrollBackBtn = document.getElementById('scroll-back-btn');
    this.flagHud = document.getElementById('flag-hud');
    this.stepCounter = document.getElementById('step-counter');
    this.finalAlt = document.getElementById('final-alt');
    this.bestAlt = document.getElementById('best-alt');
    this.deathCause = document.getElementById('death-cause');
    this.loreCount = document.getElementById('lore-count');

    // High Score Persistence
    this.bestSteps = parseInt(localStorage.getItem('nightclimb_steps') || '0', 10);

    this.initEvents();
    requestAnimationFrame((t) => this.loop(t));
  }

  initEvents() {
    this.startBtn.addEventListener('click', () => {
      window.soundEngine?.ensureContext();
      this.startGame();
    });

    this.retryBtn.addEventListener('click', () => {
      this.startGame();
    });

    // Clicking Flag opens the Ancient Scroll (Image 5!)
    this.flagHud.addEventListener('click', () => {
      if (this.state === 'PLAYING') {
        this.openScroll();
      }
    });

    this.scrollBackBtn.addEventListener('click', () => {
      this.closeScroll();
    });

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        if (this.state === 'TITLE' || this.state === 'GAMEOVER') {
          window.soundEngine?.ensureContext();
          this.startGame();
        }
      } else if (e.code === 'KeyL') {
        if (this.state === 'PLAYING') {
          this.openScroll();
        } else if (this.state === 'SCROLL') {
          this.closeScroll();
        }
      } else if (e.code === 'Escape') {
        if (this.state === 'SCROLL') {
          this.closeScroll();
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
    this.scrollModal.classList.add('hidden');

    // Show initial verse snippet
    this.loreManager.checkMilestone(0);
  }

  openScroll() {
    this.prevState = this.state;
    this.state = 'SCROLL';
    this.loreManager.openScroll();
  }

  closeScroll() {
    this.loreManager.closeScroll();
    this.state = this.prevState || 'PLAYING';
  }

  gameOver(cause) {
    this.state = 'GAMEOVER';
    this.player.die(cause);

    const steps = Math.floor(this.player.highestAltitude * 5); // Scale altitude into steps
    if (steps > this.bestSteps) {
      this.bestSteps = steps;
      localStorage.setItem('nightclimb_steps', this.bestSteps.toString());
    }

    setTimeout(() => {
      this.finalAlt.textContent = `${steps} 👣`;
      this.bestAlt.textContent = `${this.bestSteps} 👣`;
      this.deathCause.textContent = cause;
      this.loreCount.textContent = `${this.loreManager.getUnlockedCount()} / ${this.loreManager.getTotalCount()}`;

      this.gameoverScreen.classList.remove('hidden');
      this.gameoverScreen.classList.add('active');
    }, 1100);
  }

  loop(currentTime) {
    const dt = Math.min((currentTime - this.lastTime) / 1000, 0.1);
    this.lastTime = currentTime;

    if (this.state === 'PLAYING') {
      this.input.update(dt);
      this.player.update(dt);
      this.obstacleManager.update(dt, this.player.altitude);

      // Check poetry stanza unlock
      this.loreManager.checkMilestone(this.player.altitude);

      // Check trap collision
      const collision = this.obstacleManager.checkCollision(this.player);
      if (collision.isHit) {
        this.gameOver(collision.cause);
      }

      // Update Flag Step Counter in HUD (Matches screenshot!)
      const currentSteps = Math.max(0, Math.floor(this.player.altitude * 5));
      this.stepCounter.textContent = currentSteps.toString();
    } else if (this.state === 'GAMEOVER') {
      this.player.update(dt);
    }

    // Render Scene with 1-Bit Bayer Dither pass
    this.renderer.render(this.player, this.obstacleManager, dt);

    requestAnimationFrame((t) => this.loop(t));
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.game = new Game();
});
