// Lore of the Dark Spire - Milestone Fragments
const TOWER_LORE = [
  {
    altitude: 25,
    title: "Canto I: The First Step",
    text: "He who seeks the crown of stars must tread upon cold stone, unblessed and alone."
  },
  {
    altitude: 75,
    title: "Canto II: The Slumbering Spire",
    text: "The spiral has no beginning, nor does the stone remember those who bled before."
  },
  {
    altitude: 150,
    title: "Canto III: Cold Steel",
    text: "The blades swing true in the black wind, blind to prayer, deaf to grief."
  },
  {
    altitude: 250,
    title: "Canto IV: Falling Foundations",
    text: "Tread softly, wanderer; the stair yields beneath the weight of hesitation."
  },
  {
    altitude: 400,
    title: "Canto V: Eyes in the Mist",
    text: "Stone gargoyles watch your ascent, measuring each breath before the void claims it."
  },
  {
    altitude: 600,
    title: "Canto VI: The Whispering Zenith",
    text: "Higher still, where the air turns to frost and shadows cast their own light."
  },
  {
    altitude: 850,
    title: "Canto VII: The Iron Decree",
    text: "None who reach the clouds remain mortal; their marrow becomes the spire's mortar."
  },
  {
    altitude: 1200,
    title: "Canto VIII: The Void's Embrace",
    text: "Look not down, for the abyss looks back, wearing the face of Roland."
  }
];

class LoreManager {
  constructor() {
    this.unlocked = new Set();
    this.currentLore = null;
    this.bannerTimer = null;
  }

  checkMilestone(altitude) {
    for (const item of TOWER_LORE) {
      if (altitude >= item.altitude && !this.unlocked.has(item.altitude)) {
        this.unlocked.add(item.altitude);
        this.showLore(item);
        if (window.soundEngine) window.soundEngine.playLoreChime();
        return item;
      }
    }
    return null;
  }

  showLore(item) {
    const banner = document.getElementById('lore-banner');
    const textEl = document.getElementById('lore-text');
    if (!banner || !textEl) return;

    textEl.textContent = `"${item.text}" — ${item.title}`;
    banner.classList.remove('hidden');

    if (this.bannerTimer) clearTimeout(this.bannerTimer);
    this.bannerTimer = setTimeout(() => {
      banner.classList.add('hidden');
    }, 6000);
  }

  getUnlockedCount() {
    return this.unlocked.size;
  }

  getTotalCount() {
    return TOWER_LORE.length;
  }
}

window.loreManager = new LoreManager();

