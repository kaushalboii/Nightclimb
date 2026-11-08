// Player (Roland / The Wanderer)
class Player {
  constructor() {
    this.altitude = 0.0;
    this.targetAltitude = 0.0;
    this.velocity = 0;
    this.isAlive = true;
    this.deathTimer = 0;
    this.lastStepAltitude = 0;
    this.direction = 1; // 1 = up, -1 = down
    this.walkCycle = 0;
    this.highestAltitude = 0;
  }

  reset() {
    this.altitude = 0.0;
    this.targetAltitude = 0.0;
    this.velocity = 0;
    this.isAlive = true;
    this.deathTimer = 0;
    this.lastStepAltitude = 0;
    this.direction = 1;
    this.walkCycle = 0;
    this.highestAltitude = 0;
  }

  addDelta(deltaMeters) {
    if (!this.isAlive) return;
    
    // Prevent descending below base ground (altitude 0)
    const newTarget = this.targetAltitude + deltaMeters;
    this.targetAltitude = Math.max(0, newTarget);

    if (Math.abs(deltaMeters) > 0.001) {
      this.direction = Math.sign(deltaMeters);
    }
  }

  update(dt) {
    if (!this.isAlive) {
      this.deathTimer += dt;
      return;
    }

    // Smooth responsive tracking towards target altitude
    const diff = this.targetAltitude - this.altitude;
    this.velocity = diff * 14.0;
    this.altitude += this.velocity * dt;

    if (this.altitude > this.highestAltitude) {
      this.highestAltitude = this.altitude;
    }

    // Continuous walking animation tied directly to climbing speed
    const speed = Math.abs(this.velocity);
    if (speed > 0.02) {
      this.walkCycle += speed * dt * 5.0;

      // Trigger footstep sound per stone step
      const stepDist = Math.abs(this.altitude - this.lastStepAltitude);
      if (stepDist >= 0.2) {
        this.lastStepAltitude = this.altitude;
        window.soundEngine?.playStep();
      }
    }
  }

  die(cause) {
    if (!this.isAlive) return;
    this.isAlive = false;
    this.deathTimer = 0;
    window.soundEngine?.playDeath();
  }
}

window.player = new Player();

