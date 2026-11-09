/**
 * A Fool's Errand - Game Configuration
 * All constants, frame URLs, story beats, and game balance values
 */

export const CONFIG = {
  // Game identity
  GAME_TITLE: "A Fool's Errand",
  SUBTITLE: "The Dark Tower Ascent",
  POET: "R. Browning",
  EST_YEAR: 1843,

  // Virtual resolution for internal logic
  VIRTUAL_WIDTH: 310,
  VIRTUAL_HEIGHT: 552, // 9:16 aspect ratio

  // Frame URLs (7 frames for smooth animation cycle)
  // Using the provided Google Images URLs
  FRAMES: [
    "https://lh3.googleusercontent.com/aida-public/AB6AXuD83grN85lJ8pkveIpnxH7zgtL0vj1dSqIgeOw8D2EDwxi9OCeFoHTSk6iVEM5CTIAEVNd37dWI-Jiul62x356AHv5kYuVoZMsVAOAQ34a4txb02y7nYXwcxmYOeka6UQG9YdOMcK-aUUlmTmn64AyJI8GbYXkvKqQYNH0OhfC0yHqb_NfZqGyDhT-tAESOLBOgDv4KAXUMNhe2xsWazgYCekJtYmnxfxIgu6fwaYxRS_SIJPpUIHsr", // Frame 0: Title/Initial step
    "https://lh3.googleusercontent.com/aida-public/AB6AXuA7QYm8OhEP9f1mVBGvlEX4fPRpf-IPJ6_VKMfMEgHT7LyClLaDHAmUOttGboixvQ0qwuyZUQ9CoIXl3Nv_1XkIL5Dw37Sj1qJjDFKgW5T1-SBL5ZAq3UPKU-dQSyRUd0fdIVu-vTVVCbxBoDFimpU_OtJC6X9HnZHbiQuagQ1FybdDqQegm83Qex-d15tPbvaDbigOolWuUmkxe49fwhWjlJMD4s6Ra3o6L7tNP9HIBScg9UHHWUN-", // Frame 1: Ascent entrance
    "https://lh3.googleusercontent.com/aida-public/AB6AXuCrkqr0nusvYmS8OSLhE--lz1T_2nqoWCFvgdLWUUSWEI0s2KegVgPlQ8fberXZe4uW0DFAGgi0hT7YDjqHqp4DUzxJScAUWLj0iz-7y41jc06g2VU7VliHjUxL3qJsIoPrZQHGKf7mVq2VjmAAmcIjB4qfd3eitLErD57y05DI3JJUkYs5pSr-bECH8OQ2_XwW3PIkq3BQdLUT-_-rJyZBFhYsSA70m9yoWgKmJ3DCEw6VWUvOP-hj", // Frame 2: Inside spiral masonry
    "https://lh3.googleusercontent.com/aida-public/AB6AXuD26gsfd2OBEwnSLcNl8BJIds4UFWZEkQiW1G3nGegvd8kbwkEU9Kby6imvBtcNYp82EFA5S1hxUpxd_7PfxxJi3TIbkmhbC7gNLEhmRpeoQpzYgJt69dykYqFeAnbJklLsPC1hpNIrttvI2oFoHMxKRyKnY8HAwAeQNrgWp-hairwPWTDj4AGVyHo5b1_wqejLniWMinPScv3VrSR5eLkdtaaqQq41Qd_QUrGnv2sHs7AqyXI9h_Pm", // Frame 3: Vaulted passage
    "https://lh3.googleusercontent.com/aida-public/AB6AXuAWsRO0svrDP0M1CXbRF0pgQE6Hi02L_khpS2OkM4JBB4TMW--NnFKrvRfJJorgRh_SiSdInIxTuaSFMB2DErKt1zv6bOpWBoYiTOESvHJjAfKeobViWl0uEZg5L4ydQbGhW7f01GxG358TmmIxD7vCUi6f4n4c3uNJpquw_NzsoyudKl4-Rw5PGk3X6bS34K3v8MkVF67HPPNbQEeHVmIdKcHgUqd4zmKsv1V36ox-h-WKRqsyuBUT", // Frame 4: Steep winding stairs
    "https://lh3.googleusercontent.com/aida-public/AB6AXuA8SKEj8tMx-E2EmFyO7Px-AID5qbTbb5iyU1O1fUdYApWEMkU85o6cZRUZ5C_4twPnLPAX-bCyrHYT6oUUoVGW4CLY2G58-LYYCzGF1IP87j_DoKS98tAn682AqtyBz_mJqSLT4iJJVPPqrd1HjNkZjAcx42EzXxetjTG4RRPGmAwWFkQMuR1scfHuceJmOHxxvnMLjMaVLJ3Rc-x3FG615k7bFxC054DW7O4wth1R5Unyst0pYZnz", // Frame 5: Rolled barrel coming down
    "https://lh3.googleusercontent.com/aida-public/AB6AXuD83grN85lJ8pkveIpnxH7zgtL0vj1dSqIgeOw8D2EDwxi9OCeFoHTSk6iVEM5CTIAEVNd37dWI-Jiul62x356AHv5kYuVoZMsVAOAQ34a4txb02y7nYXwcxmYOeka6UQG9YdOMcK-aUUlmTmn64AyJI8GbYXkvKqQYNH0OhfC0yHqb_NfZqGyDhT-tAESOLBOgDv4KAXUMNhe2xsWazgYCekJtYmnxfxIgu6fwaYxRS_SIJPpUIHsr"  // Frame 6: Loop back to frame 0 variant (or could be distinct)
  ],

  // Frame indices for special situations
  FRAME_INDICES: {
    DEFAULT: 0,
    BARREL_WARNING: 5,      // Frame showing barrel
    BARREL_ACTIVE: 5,       // During barrel roll
    BARREL_AFTERMATH: 4,    // After barrel passes
    DEATH: 5                // Death frame
  },

  // Frame animation timing
  FRAME_CYCLE_INTERVAL: 12,    // Steps per frame advance (slower = more cinematic)
  FRAME_TRANSITION_MS: 200,    // Crossfade duration
  VERTICAL_BOB_AMPLITUDE: 3,   // Pixels of vertical head-bob
  VERTICAL_BOB_FREQUENCY: 0.5, // Cycles per step

  // Lane system
  LANES: {
    LEFT: -1,
    MID: 0,
    RIGHT: 1
  },
  LANE_NAMES: { '-1': 'LEFT', '0': 'MID', '1': 'RIGHT' },
  LANE_OFFSETS: { '-1': -75, '0': 0, '1': 75 }, // Pixel offsets for barrel positioning

  // Player stats
  STARTING_ALTITUDE: 1843,
  STARTING_TORCHES: 3,
  MAX_TORCHES: 3,
  CHECKPOINT_INTERVAL: 300, // Steps between checkpoints

  // Barrel hazard configuration
  BARREL: {
    MIN_ALTITUDE_TO_SPAWN: 300,
    BASE_SPAWN_CHANCE: 0.06,   // Per step chance
    CHANCE_INCREASE_PER_100_STEPS: 0.008,
    MAX_SPAWN_CHANCE: 0.18,
    SPEED: 0.022,              // Progress per frame (lower = slower)
    COLLISION_WINDOW_START: 0.68, // Progress where collision check starts
    COLLISION_WINDOW_END: 0.88,   // Progress where collision check ends
    WARNING_DURATION_MS: 1500, // How long warning shows before barrel
    LANE_CHOICES: [-1, 0, 1]
  },

  // Step climbing
  STEP: {
    BASE_INCREMENT: 1,
    WHEEL_MULTIPLIER: 1,
    SWIPE_THRESHOLD: 25,       // Pixels for swipe up
    SWIPE_HORIZONTAL_THRESHOLD: 40, // Pixels for swipe left/right
    KEYBOARD_REPEAT_DELAY: 120, // ms
    KEYBOARD_REPEAT_RATE: 60   // ms
  },

  // Story beats (from Browning's "Childe Roland to the Dark Tower Came")
  STORY_BEATS: [
    { step: 0,    act: "ACT I · THE DESOLATE GATE", poem: "My first thought was, he lied in every word..." },
    { step: 250,  act: "ACT I · THE DESOLATE GATE", poem: "For mark! no sooner was I fairly found pledged to the plain, after a pace or two..." },
    { step: 500,  act: "ACT II · THE WINDING STAIRS", poem: "Gray plain all round: nothing but plain to the horizon's bound. I might go on; nought else remained to do." },
    { step: 900,  act: "ACT II · THE WINDING STAIRS", poem: "So, on I went. I think I never saw such starved ignoble nature; nothing throve." },
    { step: 1300, act: "ACT III · THE TRAP OF ROLLED OAK", poem: "A sudden little river crossed my path... As for the grass, it grew as scant as hair in leprosy." },
    { step: 1800, act: "ACT III · THE TRAP OF ROLLED OAK", poem: "What bad use was that engine for? To wheel men's bodies into the dark void!" },
    { step: 2200, act: "ACT IV · THE BLIND SPIRE", poem: "The round squat turret, blind as the fool's heart, built of brown stone, without a counterpart!" },
    { step: 2700, act: "ACT IV · THE DARK TOWER REACHED", poem: "And yet dauntless the slug-horn to my lips I set, and blew: 'Childe Roland to the Dark Tower came.'" }
  ],

  // Rank progression
  RANKS: [
    { minStep: 0,    title: "RANK: VAGRANT" },
    { minStep: 500,  title: "RANK: PILGRIM" },
    { minStep: 1200, title: "RANK: SQUIRE" },
    { minStep: 2000, title: "RANK: CHILDE ROLAND" },
    { minStep: 3000, title: "RANK: TOWER WALKER" }
  ],

  // Audio
  AUDIO: {
    STEP_FREQ_START: 110,
    STEP_FREQ_END: 30,
    STEP_DURATION: 0.08,
    EVADE_FREQ_START: 350,
    EVADE_FREQ_END: 600,
    EVADE_DURATION: 0.09,
    WARNING_FREQ_START: 140,
    WARNING_FREQ_END: 90,
    WARNING_DURATION: 0.2,
    IMPACT_FREQ_START: 90,
    IMPACT_FREQ_END: 20,
    IMPACT_DURATION: 0.35,
    CRANK_CLICK_FREQ: 800,
    CRANK_CLICK_DURATION: 0.02
  },

  // Visual effects
  EFFECTS: {
    SCREEN_SHAKE_INTENSITY: 10,
    SCREEN_SHAKE_DURATION: 100,
    DODGE_TAG_DURATION: 500,
    DODGE_TILT_MAX: 32,      // Max pixel offset for lane shift
    DODGE_RETURN_DURATION: 300,
    LANE_INDICATOR_FLASH_MS: 150
  },

  // Persistence keys
  STORAGE_KEYS: {
    CHECKPOINT: 'fools_errand_checkpoint',
    TORCHES: 'fools_errand_torches',
    HIGH_SCORE: 'fools_errand_high_score',
    TOTAL_STEPS: 'fools_errand_total_steps',
    SETTINGS: 'fools_errand_settings',
    BEST_ALTITUDE: 'fools_errand_best_altitude'
  },

  // Default settings
  DEFAULT_SETTINGS: {
    sfxEnabled: true,
    crtEnabled: true,
    screenShakeEnabled: true
  }
};

// Helper to get current story beat
export function getStoryBeat(currentStep) {
  let activeBeat = CONFIG.STORY_BEATS[0];
  for (const beat of CONFIG.STORY_BEATS) {
    if (currentStep >= beat.step) {
      activeBeat = beat;
    } else {
      break;
    }
  }
  return activeBeat;
}

// Helper to get current rank
export function getRank(currentStep) {
  let currentRank = CONFIG.RANKS[0];
  for (const rank of CONFIG.RANKS) {
    if (currentStep >= rank.minStep) {
      currentRank = rank;
    } else {
      break;
    }
  }
  return currentRank.title;
}

// Helper to calculate barrel spawn chance at current altitude
export function getBarrelSpawnChance(altitude) {
  const stepsAboveMin = Math.max(0, altitude - CONFIG.BARREL.MIN_ALTITUDE_TO_SPAWN);
  const hundreds = stepsAboveMin / 100;
  const chance = CONFIG.BARREL.BASE_SPAWN_CHANCE + (hundreds * CONFIG.BARREL.CHANCE_INCREASE_PER_100_STEPS);
  return Math.min(chance, CONFIG.BARREL.MAX_SPAWN_CHANCE);
}