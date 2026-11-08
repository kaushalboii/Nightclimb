// Stanzas from Robert Browning's "Childe Roland to the Dark Tower Came"
const CHILDE_ROLAND_POEM = [
  {
    numeral: "I",
    altitude: 10,
    lines: [
      "My first thought was, he",
      "lied in every word,",
      "",
      "that hoary cripple, with",
      "malicious eye",
      "",
      "askance to watch the",
      "working of his lie",
      "",
      "on mine, and mouth scarce",
      "able to afford",
      "",
      "suppression of the glee that",
      "pursed and scored",
      "",
      "its edge at one more victim",
      "gained thereby."
    ],
    snippet: "My first thought was, he lied in every word,"
  },
  {
    numeral: "II",
    altitude: 60,
    lines: [
      "What else should he have done?",
      "For mark! no sooner",
      "",
      "was I fairly found pledged",
      "to the plain, after a world of sighs,",
      "",
      "than I turned into that ominous",
      "tract which, all agree,",
      "",
      "hides the Dark Tower.",
      "Yet destitute of pride,",
      "",
      "glad was the spirit that now",
      "ceased to pine."
    ],
    snippet: "Glad was the spirit that now ceased to pine."
  },
  {
    numeral: "III",
    altitude: 140,
    lines: [
      "So, on I went. I think I never",
      "saw such starved ignoble nature;",
      "",
      "nothing throve:",
      "for flowers, as well expect",
      "a cedar grove!",
      "",
      "No! penury, inertness and grimace,",
      "in some strange sort, were the land's",
      "portion. 'See Or shut your eyes,'",
      "",
      "said Nature peevishly,",
      "'it nothing skills.'"
    ],
    snippet: "I think I never saw such starved ignoble nature."
  },
  {
    numeral: "IV",
    altitude: 250,
    lines: [
      "A sudden little river",
      "crossed my path",
      "",
      "as unexpected as a serpent",
      "comes. No sluggish tide",
      "",
      "could have such black",
      "and furious spite:",
      "",
      "which poured along, yet",
      "seemed no deeper than a man's",
      "throat could quench."
    ],
    snippet: "A sudden little river crossed my path."
  },
  {
    numeral: "V",
    altitude: 400,
    lines: [
      "What in the midst was dumb?",
      "A tall black spire,",
      "",
      "blind as the fool's heart,",
      "built of round rock,",
      "",
      "without a counterpart",
      "in the whole world.",
      "",
      "The point of hope, the",
      "zenith of despair."
    ],
    snippet: "A tall black spire, blind as the fool's heart."
  },
  {
    numeral: "VI",
    altitude: 600,
    lines: [
      "And yet Dauntless the",
      "slug-horn to my lips I set,",
      "",
      "and blew. 'Childe Roland",
      "to the Dark Tower came.'"
    ],
    snippet: "And blew: 'Childe Roland to the Dark Tower came.'"
  }
];

class LoreManager {
  constructor() {
    this.unlocked = [];
    this.currentStanza = null;
    this.isScrollOpen = false;
  }

  checkMilestone(altitude) {
    for (const item of CHILDE_ROLAND_POEM) {
      if (altitude >= item.altitude && !this.unlocked.find(u => u.numeral === item.numeral)) {
        this.unlocked.push(item);
        this.currentStanza = item;
        this.updatePoemSnippet(item);
        window.soundEngine?.playLoreChime();
        return item;
      }
    }
    return null;
  }

  updatePoemSnippet(item) {
    const snippetEl = document.getElementById('poem-snippet');
    if (snippetEl) {
      const line1 = item.lines[0] || "";
      const line2 = item.lines[1] || "";
      snippetEl.innerHTML = `${line1}<br>${line2}`;
      snippetEl.classList.remove('fade-out');
    }
  }

  openScroll(index = -1) {
    const modal = document.getElementById('scroll-modal');
    if (!modal) return;

    const stanza = (index >= 0 && index < this.unlocked.length) 
      ? this.unlocked[index] 
      : (this.currentStanza || CHILDE_ROLAND_POEM[0]);

    document.getElementById('scroll-numeral').textContent = stanza.numeral;
    const bodyEl = document.getElementById('scroll-body');
    bodyEl.innerHTML = stanza.lines.map(l => l === "" ? "<br>" : `<div class="scroll-line">${l}</div>`).join('');

    modal.classList.remove('hidden');
    this.isScrollOpen = true;
  }

  closeScroll() {
    const modal = document.getElementById('scroll-modal');
    if (modal) modal.classList.add('hidden');
    this.isScrollOpen = false;
  }

  getUnlockedCount() {
    return this.unlocked.length;
  }

  getTotalCount() {
    return CHILDE_ROLAND_POEM.length;
  }
}

window.loreManager = new LoreManager();
