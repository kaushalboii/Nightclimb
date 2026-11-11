# Nightclimb (The Infinite Spiral Ascent)

A monochrome, 1-bit precision tower climber inspired by **[A Fool's Errand](https://apps.apple.com/us/app/a-fools-errand/id6812658213)** (IORAMA).

---

## 🕹️ Gameplay & Core Mechanics

- **1D Spiral Ascent**: Your position is tied to a continuous spiral track wrapping around an infinite gothic dark tower.
- **Physical "Cranking" Controls**:
  - **Mouse Wheel / Trackpad**: Scroll up/down to advance/backtrack (mimicking the Playdate crank & Apple Watch Digital Crown).
  - **Swipe / Drag**: Direct vertical finger or mouse scrubbing.
  - **Interactive Virtual Crank**: On-screen circular crank dial in the bottom-right corner with realistic mechanical ratchet clicks.
  - **Keyboard**: `W` / `S` or `↑` / `↓` arrow keys.
- **Deadly Hazards**:
  - **Spike Traps**: Cycle through dormant, warning rumble, and lethal extension.
  - **Pendulum Scythes**: Huge crescent blades swinging rhythmically across the stairs.
  - **Crumbling Stones**: Steps that fracture and collapse into the abyss 0.8 seconds after being stepped on.
  - **Gargoyles**: Wall-mounted stone beasts that blast dark fire and embers.
- **Dark Tower Lore**: Every 50–100m, ancient stanzas of the Dark Spire poem unlock.
- **Synthesized Web Audio**: Footsteps, mechanical ratchet ticks, wind drone, spike snaps, whooshing blades, and gothic chime bells generated entirely via the Web Audio API (zero external audio files required).

---

## 🚀 How to Play Right Now (Web)

You can launch the game directly in any browser:

```bash
# Option 1: Direct open on macOS
open index.html

# Option 2: Local HTTP server
python3 -m http.server 8080
# Then open http://localhost:8080 in Chrome or Safari
```

---

## 📱 Cross-Platform Path (Web ➔ iOS & Android)

Because the game is built using standard responsive HTML5 Canvas and vanilla JavaScript with zero heavy dependencies:

### 1. Capacitor (Fastest Path to iOS App Store & Google Play)
You can wrap this web game into native iOS and Android binaries in minutes:
```bash
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android
npx cap init Nightclimb com.nightclimb.game --web-dir .
npx cap add ios
npx cap add android
npx cap open ios      # Opens Xcode
npx cap open android  # Opens Android Studio
```

### 2. Apple Watch Companion App (Digital Crown)
To match *A Fool's Errand*'s signature Apple Watch mode:
- Add a watchOS target in the Xcode project.
- Use `WKInterfaceCrownSequencer` to bind crown rotation directly to `altitude` and send micro-haptic taps with `WKInterfaceDevice.current().play(.click)`.

 
