// Obstacle & Trap System for Nightclimb
// Matches Iorama's "A Fool's Errand" traps (Barrels, Spikes, Ghosts, Crumbling steps)

class ObstacleManager {
  constructor() {
    this.obstacles = [];
    this.nextSpawnAltitude = 8.0; // Start obstacles early
    this.generatedUpTo = 0;
    this.dodgedCount = 0;
  }

  reset() {
    this.obstacles = [];
    this.nextSpawnAltitude = 8.0;
    this.generatedUpTo = 0;
    this.dodgedCount = 0;
  }

  update(dt, playerAltitude) {
    // Generate ahead of player
    while (this.generatedUpTo < playerAltitude + 30) {
      this.generateNext();
    }

    // Clean up old obstacles far below
    this.obstacles = this.obstacles.filter(obs => {
      if (obs.altitude < playerAltitude - 15) {
        if (!obs.passed) {
          obs.passed = true;
          this.dodgedCount++;
        }
        return false;
      }
      return true;
    });

    for (const obs of this.obstacles) {
      obs.update(dt, playerAltitude);
    }
  }

  generateNext() {
    const startAlt = Math.max(this.nextSpawnAltitude, this.generatedUpTo);
    const difficulty = Math.min(startAlt / 200.0, 1.0);

    // Trap types from A Fool's Errand:
    // BARREL: Rolling down steps
    // SPIKE: Popping out of stone
    // GHOST: Floating spirit
    // CRUMBLE: Fracturing steps
    const types = ['BARREL', 'SPIKE'];
    if (startAlt > 18) types.push('GHOST');
    if (startAlt > 35) types.push('CRUMBLE');

    const chosen = types[Math.floor(Math.random() * types.length)];
    const gap = 4.5 - difficulty * 1.8 + Math.random() * 2.0;

    let obs = null;
    switch (chosen) {
      case 'BARREL':
        obs = new BarrelTrap(startAlt);
        break;
      case 'SPIKE':
        obs = new SpikeTrap(startAlt);
        break;
      case 'GHOST':
        obs = new GhostTrap(startAlt);
        break;
      case 'CRUMBLE':
        obs = new CrumbleTrap(startAlt);
        break;
    }

    if (obs) this.obstacles.push(obs);

    this.nextSpawnAltitude = startAlt + gap;
    this.generatedUpTo = startAlt + gap;
  }

  checkCollision(player) {
    for (const obs of this.obstacles) {
      if (obs.checkHit(player)) {
        return { isHit: true, cause: obs.deathMessage };
      }
    }
    return { isHit: false, cause: null };
  }
}

// 1. Rolling Powder Keg / Barrel (Screenshot 2)
class BarrelTrap {
  constructor(altitude) {
    this.type = 'BARREL';
    this.altitude = altitude;
    this.rollSpeed = 2.4; // Rolls downward along spiral
    this.angle = 0;
    this.deathMessage = "Crushed by a rolling powder keg";
  }

  update(dt, playerAltitude) {
    // Barrel rolls DOWN the stairs towards player
    this.altitude -= this.rollSpeed * dt;
    this.angle += dt * 6.0; // rotation
  }

  checkHit(player) {
    const dist = Math.abs(player.altitude - this.altitude);
    return dist < 0.65;
  }
}

// 2. Popping Floor Spikes (Screenshots 3 & 4)
class SpikeTrap {
  constructor(altitude) {
    this.type = 'SPIKE';
    this.altitude = altitude;
    this.width = 1.0;
    this.period = 2.4 + Math.random() * 0.8;
    this.timer = Math.random() * this.period;
    this.state = 'DORMANT';
    this.spikeHeight = 0;
    this.deathMessage = "Impaled upon rusted spikes";
    this.warnSoundPlayed = false;
    this.snapSoundPlayed = false;
  }

  update(dt, playerAltitude) {
    this.timer = (this.timer + dt) % this.period;
    const p = this.timer / this.period;

    if (p < 0.55) {
      this.state = 'DORMANT';
      this.spikeHeight = 0;
      this.warnSoundPlayed = false;
      this.snapSoundPlayed = false;
    } else if (p < 0.72) {
      this.state = 'WARNING';
      this.spikeHeight = 0.25 + Math.sin(this.timer * 40) * 0.1;
      if (!this.warnSoundPlayed && Math.abs(playerAltitude - this.altitude) < 8) {
        window.soundEngine?.playTrapWarning();
        this.warnSoundPlayed = true;
      }
    } else if (p < 0.94) {
      this.state = 'EXTENDED';
      this.spikeHeight = 1.0;
      if (!this.snapSoundPlayed && Math.abs(playerAltitude - this.altitude) < 8) {
        window.soundEngine?.playSpikeSnap();
        this.snapSoundPlayed = true;
      }
    } else {
      this.state = 'RETRACTING';
      this.spikeHeight = 0.3;
    }
  }

  checkHit(player) {
    if (this.state === 'EXTENDED') {
      const dist = Math.abs(player.altitude - this.altitude);
      return dist < this.width * 0.5;
    }
    return false;
  }
}

// 3. Floating Ghost / Spire Wraith (Screenshot 4)
class GhostTrap {
  constructor(altitude) {
    this.type = 'GHOST';
    this.altitude = altitude;
    this.bobTimer = Math.random() * Math.PI * 2;
    this.floatOffset = 0;
    this.deathMessage = "Touched by the wandering spire wraith";
  }

  update(dt, playerAltitude) {
    this.bobTimer += dt * 3.0;
    this.floatOffset = Math.sin(this.bobTimer) * 0.4;
  }

  checkHit(player) {
    const dist = Math.abs(player.altitude - (this.altitude + this.floatOffset));
    return dist < 0.7;
  }
}

// 4. Crumbling Stone Step
class CrumbleTrap {
  constructor(altitude) {
    this.type = 'CRUMBLE';
    this.altitude = altitude;
    this.isTriggered = false;
    this.triggerTimer = 0.8;
    this.isCollapsed = false;
    this.shakeOffset = 0;
    this.deathMessage = "Fell into the bottomless spire abyss";
  }

  update(dt, playerAltitude) {
    if (this.isTriggered && !this.isCollapsed) {
      this.triggerTimer -= dt;
      this.shakeOffset = (Math.random() * 2 - 1) * 3;
      if (this.triggerTimer <= 0) {
        this.isCollapsed = true;
        if (Math.abs(playerAltitude - this.altitude) < 8) {
          window.soundEngine?.playCrumble();
        }
      }
    }
  }

  checkHit(player) {
    const dist = Math.abs(player.altitude - this.altitude);
    if (dist < 0.6) {
      if (!this.isTriggered) this.isTriggered = true;
      if (this.isCollapsed) return true;
    }
    return false;
  }
}

window.obstacleManager = new ObstacleManager();
