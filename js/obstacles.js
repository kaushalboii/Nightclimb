// Obstacle & Trap System for Nightclimb
class ObstacleManager {
  constructor() {
    this.obstacles = [];
    this.nextSpawnAltitude = 12.0; // Start traps after a peaceful tutorial climb
    this.generatedUpTo = 0;
    this.dodgedCount = 0;
  }

  reset() {
    this.obstacles = [];
    this.nextSpawnAltitude = 12.0;
    this.generatedUpTo = 0;
    this.dodgedCount = 0;
  }

  update(dt, playerAltitude) {
    // Generate new obstacles ahead of player
    while (this.generatedUpTo < playerAltitude + 30) {
      this.generateChunk();
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

    // Update trap internal state / cycles
    for (const obs of this.obstacles) {
      obs.update(dt, playerAltitude);
    }
  }

  generateChunk() {
    const startAlt = Math.max(this.nextSpawnAltitude, this.generatedUpTo);
    const difficulty = Math.min(startAlt / 250.0, 1.0); // 0.0 to 1.0

    // Choose obstacle type
    const types = ['SPIKE', 'PENDULUM'];
    if (startAlt > 25) types.push('CRUMBLE');
    if (startAlt > 60) types.push('GARGOYLE');

    const chosenType = types[Math.floor(Math.random() * types.length)];
    let gap = 5.0 - difficulty * 2.2 + (Math.random() * 2.0); // 2.5m - 5m spacing

    let obs = null;
    switch (chosenType) {
      case 'SPIKE':
        obs = new SpikeTrap(startAlt);
        break;
      case 'PENDULUM':
        obs = new PendulumTrap(startAlt);
        break;
      case 'CRUMBLE':
        obs = new CrumbleTrap(startAlt);
        break;
      case 'GARGOYLE':
        obs = new GargoyleTrap(startAlt);
        break;
    }

    if (obs) {
      this.obstacles.push(obs);
    }

    this.nextSpawnAltitude = startAlt + gap;
    this.generatedUpTo = startAlt + gap;
  }

  checkCollision(player) {
    for (const obs of this.obstacles) {
      const hit = obs.checkHit(player);
      if (hit) {
        return { isHit: true, cause: obs.deathMessage };
      }
    }
    return { isHit: false, cause: null };
  }
}

// 1. Spike Trap
class SpikeTrap {
  constructor(altitude) {
    this.type = 'SPIKE';
    this.altitude = altitude;
    this.width = 1.2; // Width in meters along the path
    this.period = 2.4 + Math.random() * 0.8; // Cycle duration
    this.timer = Math.random() * this.period;
    this.state = 'DORMANT'; // DORMANT, WARNING, EXTENDED
    this.spikeHeight = 0; // 0 to 1
    this.deathMessage = "Impaled upon rusted spikes";
    this.warnSoundPlayed = false;
    this.snapSoundPlayed = false;
  }

  update(dt, playerAltitude) {
    this.timer = (this.timer + dt) % this.period;
    const progress = this.timer / this.period;

    // 0.0 - 0.5: Dormant
    // 0.5 - 0.7: Warning (spikes shake/peek)
    // 0.7 - 0.95: Extended (Lethal!)
    // 0.95 - 1.0: Retract
    if (progress < 0.55) {
      this.state = 'DORMANT';
      this.spikeHeight = 0;
      this.warnSoundPlayed = false;
      this.snapSoundPlayed = false;
    } else if (progress < 0.72) {
      this.state = 'WARNING';
      this.spikeHeight = 0.2 + Math.sin(this.timer * 40) * 0.08;
      if (!this.warnSoundPlayed && Math.abs(playerAltitude - this.altitude) < 8) {
        window.soundEngine?.playTrapWarning();
        this.warnSoundPlayed = true;
      }
    } else if (progress < 0.94) {
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
      if (dist < this.width * 0.45) {
        return true;
      }
    }
    return false;
  }
}

// 2. Pendulum Scythe
class PendulumTrap {
  constructor(altitude) {
    this.type = 'PENDULUM';
    this.altitude = altitude;
    this.width = 1.0;
    this.speed = 1.6 + Math.random() * 0.8;
    this.timer = Math.random() * Math.PI * 2;
    this.angle = 0; // -1 to 1 across path
    this.deathMessage = "Severed by the Great Pendulum";
    this.whooshPlayed = false;
  }

  update(dt, playerAltitude) {
    this.timer += dt * this.speed;
    const prevAngle = this.angle;
    this.angle = Math.sin(this.timer);

    // Play whoosh when passing near center (angle crosses 0)
    if (Math.sign(prevAngle) !== Math.sign(this.angle) && Math.abs(playerAltitude - this.altitude) < 8) {
      window.soundEngine?.playWhoosh();
    }
  }

  checkHit(player) {
    const dist = Math.abs(player.altitude - this.altitude);
    // Blade hits when passing close to middle of path (-0.28 to +0.28)
    if (dist < 0.7 && Math.abs(this.angle) < 0.28) {
      return true;
    }
    return false;
  }
}

// 3. Crumble Trap
class CrumbleTrap {
  constructor(altitude) {
    this.type = 'CRUMBLE';
    this.altitude = altitude;
    this.width = 1.4;
    this.isTriggered = false;
    this.triggerTimer = 0.85; // Seconds before collapse
    this.isCollapsed = false;
    this.shakeOffset = 0;
    this.deathMessage = "Fell into the bottomless abyss";
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
    if (dist < this.width * 0.5) {
      if (!this.isTriggered) {
        this.isTriggered = true;
      }
      if (this.isCollapsed) {
        return true; // Stepped on thin air / collapsed section
      }
    }
    return false;
  }
}

// 4. Gargoyle Fire Shooter
class GargoyleTrap {
  constructor(altitude) {
    this.type = 'GARGOYLE';
    this.altitude = altitude;
    this.width = 1.3;
    this.period = 3.2 + Math.random() * 0.6;
    this.timer = Math.random() * this.period;
    this.isBlasting = false;
    this.deathMessage = "Incinerated by stone gargoyle breath";
  }

  update(dt, playerAltitude) {
    this.timer = (this.timer + dt) % this.period;
    const progress = this.timer / this.period;

    // Blast for 25% of period
    this.isBlasting = (progress > 0.65 && progress < 0.90);
    if (this.isBlasting && Math.abs(playerAltitude - this.altitude) < 7 && Math.random() < 0.1) {
      window.soundEngine?.playTrapWarning();
    }
  }

  checkHit(player) {
    if (this.isBlasting) {
      const dist = Math.abs(player.altitude - this.altitude);
      if (dist < this.width * 0.55) {
        return true;
      }
    }
    return false;
  }
}

window.obstacleManager = new ObstacleManager();

