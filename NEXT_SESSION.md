# 🐢 TurboShells: Next Session To-Do

## Priority: Race HUD ("Juice" Layer)

### 1. Stamina Bar Overlay
```tsx
// Create: web/src/components/RaceHUD.tsx
// Use CSS transitions for smooth bar animation
<div className="stamina-bar" style={{ width: `${energyPercent}%` }} />
```
- Position: Top-left of RaceStage
- Data source: `snapshot.turtles[i].current_energy / max_energy`

### 2. Position Indicator
- Show "1st / 2nd / 3rd" badges next to each turtle
- Use `snapshot.turtles.sort((a,b) => b.x - a.x)` for rankings

### 3. Race Progress Slider
- Bottom of screen, shows distance to finish
- Width = `(leadTurtle.x / trackLength) * 100%`

### 4. Retro Typography
```css
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.race-hud {
  font-family: 'Press Start 2P', cursive;
  text-shadow: 2px 2px #000;
}
```

### 5. Pixel Art Mode
```typescript
// In RaceStage.tsx, add to app.init():
PIXI.BaseTexture.defaultOptions.scaleMode = PIXI.SCALE_MODES.NEAREST;
```

---

## Completed (This Session) ✅
- [x] Headless RaceEngine (60Hz physics)
- [x] FastAPI WebSocket bridge (30Hz broadcast)
- [x] PixiJS frontend with Paper Doll
- [x] SQLite persistence (TurtleDB, RaceResultDB)
- [x] useRoster hook + roster UI
- [x] launch.bat one-click starter

---

## Future Polish (Lower Priority)
- [ ] Camera follow (center on lead turtle)
- [ ] Dust cloud VFX on fast turtles
- [ ] Sound effects (Web Audio API)
- [ ] Main Menu dashboard
- [ ] Breeding Lab UI
