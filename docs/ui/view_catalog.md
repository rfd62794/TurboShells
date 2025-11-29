# View Catalog – Legacy Intent vs pygame_gui Implementation

Central reference linking the historical “View” specifications to their pygame_gui counterparts. Each entry tracks whether the modern panel preserves every legacy feature (layout may differ; functionality should match).

| View | Legacy Spec | pygame_gui Panel | Status | Functional Gaps / TODO |
| --- | --- | --- | --- | --- |
| Stable / Roster | `docs/UI_LAYOUT.md` §2, `docs/gdd/GDD_UI.md` §2.2 | `src/ui/panels/roster_panel.py` | **Partial** | - Missing REST / RETIRE actions in-panel.<br>- Select mode hides Active/Retired toggle entirely (legacy still allowed viewing Retired roster while selecting).<br>- Betting buttons exist but no visual indicator showing which bet is active.<br>- Start Race CTA separate from bottom nav; ensure integration with Race transition messaging. |
| Shop | `docs/UI_LAYOUT.md` §4, `technical/original_views_architecture.md` §Shop | `src/ui/panels/shop_panel.py` | **Mostly complete** | - Legacy guaranteed exactly 3 slots per refresh; current scrolling layout allows >3 simultaneously. Confirm whether economy logic still limits offerings; if not, add UI cues for the “top 3” purchasable turtles.<br>- Back button moved to header; ensure Escape/menu shortcuts still work per legacy behavior. |
| Breeding | `docs/UI_LAYOUT.md` §5, `technical/original_views_architecture.md` §Breeding | `src/ui/panels/breeding_panel.py` | **Partial** | - Parent A/B highlighting lacks the prominent “Parent 2 will be lost” X overlay.<br>- Legacy list view displayed combined active/retired order plus textual stat summary; panel currently omits stats per turtle (name only).<br>- Needs explicit warning when no roster space remains (legacy blocked BREED button with message). |
| Race HUD & Track | `docs/UI_LAYOUT.md` §3, `docs/gdd/GDD_UI.md` §2.3 | `src/ui/panels/race_hud_panel.py` (+ custom track rendering) | **Partial** | - HUD buttons function but lack hover/selected states matching legacy feedback.<br>- Progress bar currently tied to player only; legacy HUD also visualized total race completion and finish order preview.<br>- Terrain overlays still TODO per Phase 5 plan (visual segments along lanes). |

## Detailed Notes & Recommended Updates

### Stable / Roster
- **Legacy expectations:** Three vertically stacked TurtleCards with TRAIN/REST/RETIRE buttons, Active vs Retired toggle always available, Select Racer mode overlays betting buttons without removing roster browsing.
- **Panel gaps:**
  1. **REST/RETIRE** actions are missing entirely; expose buttons per slot calling the existing `RosterManager` intents.
  2. **View toggle hidden in select mode**, preventing retired roster review before choosing a racer. Consider disabling actions instead of hiding the toggle.
  3. **Bet selection feedback** should mirror legacy (highlighted border or state text). Current buttons merely set the value.
  4. **Start Race** CTA should coexist with bottom navigation (Go To Race) or clearly replace it.

### Shop
- **Legacy expectations:** Exactly three shop slots refreshed at a time, each showing turtle image, stats, price, and BUY button, plus REFRESH and BACK controls along the bottom.
- **Panel gaps:**
  1. **Inventory cardinality:** confirm that the backend still supplies three turtles; if more are provided, add UI scaffolding (pagination or “top 3 featured”) to keep the purchase loop legible.
  2. **Back navigation:** ensure header “Back” also fires the same action as the original bottom button and that ESC shortcuts map via `UIManager`.
  3. **Purchase affordability cues:** legacy UI tinted BUY buttons when funds/slots were insufficient; reproduce via disabled buttons or warning badges.

### Breeding
- **Legacy expectations:** Combined active/retired list, per-slot stats, parent highlighting (green for Parent 1, red X for Parent 2), BREED button disabled until two parents selected, plus warnings if roster full.
- **Panel gaps:**
  1. **Stat readouts:** include Swift text or reuse TurtleCard component so each candidate displays the `[ACT]/[RET] Age + stats` block.
  2. **Parent warnings:** add explicit overlay (e.g., icon or red diagonal) on Parent 2 slots plus text “Parent 2 will retire” to match the older UI.
  3. **Roster capacity validation:** before enabling BREED, check for an empty roster slot and display the legacy warning if none available.

### Race HUD
- **Legacy expectations:** Bottom HUD with 1x/2x/4x buttons centered, progress bar spanning width, header showing current bet and speed, plus (upcoming) terrain overlays along each lane.
- **Panel gaps:**
  1. **Button feedback:** add selected-state styling or toggle buttons to show the active multiplier.
  2. **Progress detail:** consider reflecting opponent progress or finish order list as in the older Race Result overlay.
  3. **Terrain visuals:** still outstanding; ensure docs note that the race track drawing layer (outside pygame_gui) must add colored segments per `UI_LAYOUT.md` guidance.

Use this catalog as the source for tracking parity work as panels evolve.
