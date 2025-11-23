# Game Design Document: Turbo Shells - Gameplay Mechanics

**Version:** 1.1 (Enhanced MVP)  
**Date:** November 22, 2025  
**Focus:** Detailed gameplay systems and mechanics

---

## 1. Turtle System

### 1.1 Core Stats

Each turtle has five core stats that affect performance:

| Stat      | Purpose                           | Effect in Race                                              |
|-----------|-----------------------------------|-------------------------------------------------------------|
| Speed     | Base movement rate                | Primary factor for forward movement                         |
| Max Energy| Total stamina capacity            | Determines how long turtle can run before resting          |
| Recovery  | Energy regeneration speed         | How quickly energy regenerates when resting                 |
| Swim      | Water terrain skill                | Multiplier applied on Water segments                       |
| Climb     | Rock terrain skill                 | Multiplier applied on Rock segments                        |

Additional identity fields:

- `name`: Chosen from a predefined list (e.g., Speedy, Tank, Nitro)
- `id`: Short unique identifier for internal tracking
- `is_active`: Boolean flag (Active vs Retired)
- `age`: Days of use (races/train sessions)
- `visual_genetics`: Color and pattern genes for future visual system

### 1.2 Movement & Energy Physics

Movement and energy are governed by shared physics in `entities.update_physics(terrain_type)`:

#### **Resting State**
- Energy regenerates based on `Recovery` and global `RECOVERY_RATE` (0.1)
- Once energy ≥ threshold (`RECOVERY_THRESHOLD * MaxEnergy`), turtle resumes running
- No forward movement while resting

#### **Running State**
- Base move speed starts from `Speed`
- Terrain modifiers apply:
  - **Grass**: neutral (Speed only)
  - **Water**: `Speed * (Swim / 10.0)`
  - **Rock**: `Speed * (Climb / 10.0)`
- Energy drains per tick: `0.5 * TERRAIN_DIFFICULTY` (0.8)
- When energy hits 0, turtle enters **resting** state

#### **Energy Mechanics**
- **Training**: Does not consume energy (by design)
- **Racing**: Energy drains continuously during movement
- **Recovery**: Passive regeneration when resting
- **Auto-Rest**: Forced rest when energy depleted

### 1.3 Training System

- **Stat Improvement**: Training improves **Speed** (MVP behavior)
- **Age Progression**: Each training session increments `Age` by 1
- **Lifecycle**: At `Age >= 100`, turtle is **auto-retired**
- **Strategic Choice**: Training improves stats but ages turtles faster

#### **Training Effects**
- Primary stat always improves by +1
- 20% chance for each other stat to improve by +1
- No energy cost (design decision for accessibility)
- Permanent stat increases

---

## 2. Breeding System

Breeding is the long-term progression system with sacrificial mechanics.

### 2.1 Eligibility & Selection

- **Any Turtle**: Active or Retired turtles can be parents
- **Two Parents Required**: Select exactly 2 parents for breeding
- **Sacrificial**: Both parents are removed from game after breeding
- **Space Requirement**: Child needs empty Active slot to succeed

### 2.2 Child Generation

#### **Stat Inheritance**
For each stat:
- **Base**: `max(parent_a.stat, parent_b.stat)` - better parent's stat
- **Mutation**: 0-20% chance of +1 or +2 (never below better parent)
- **Guaranteed Improvement**: Child always ≥ better parent for each stat

#### **Identity Creation**
- **Name**: First half of Parent A + last half of Parent B
- **Generation**: Marked as bred turtle (vs wild-caught)
- **Lineage**: Parent IDs tracked for future inheritance systems

### 2.3 Strategic Implications

- **Short-term Loss**: Sacrifice current racers for future potential
- **Long-term Gain**: Children typically exceed parents
- **Roster Management**: Must balance active team vs breeding candidates
- **Risk vs Reward**: No guaranteed improvement, but high probability

---

## 3. Economy System

### 3.1 Currency & Income

#### **Money Sources**
- **Race Prizes**: Fixed rewards for top 3 positions
  - 1st Place: $50
  - 2nd Place: $25
  - 3rd Place: $10
- **Betting Payouts**: Optional betting with risk/reward
  - Win condition: Finish 1st place
  - Payout: `bet_amount * 2`
  - Loss condition: Any other position

#### **Expenses**
- **Shop Purchases**: Buy turtles with dynamic pricing
- **Stock Refresh**: $5 to refresh shop inventory (free on first load)

### 3.2 Shop System

#### **Turtle Generation**
- **Random Stats**: Each shop turtle has randomized stat distribution
- **Dynamic Pricing**: Cost based on stat quality
  - Formula: `base_cost + scale * (Speed + normalized(MaxEnergy) + Recovery + Swim + Climb)`
  - Higher stats = higher prices
- **Limited Inventory**: 3 turtles available at any time

#### **Pricing Strategy**
- **Base Cost**: $50 for average turtles
- **Stat Scaling**: Each stat point increases price
- **Energy Normalization**: Max Energy divided by 10 to prevent domination
- **Market Balance**: Encourages strategic purchasing decisions

### 3.3 Economic Balance

#### **Money Flow**
- **Positive**: Race winnings, successful bets
- **Negative**: Turtle purchases, stock refresh
- **Break-even**: Balanced for sustainable progression

#### **Strategic Elements**
- **Roster Limits**: 3 active slots force choices
- **Investment**: Buy young turtles vs immediate needs
- **Risk Management**: Betting decisions impact cash flow

---

## 4. Racing System

### 4.1 Track Generation

#### **Terrain System**
- **Procedural Generation**: Random track segments
- **Terrain Types**: Grass (60%), Water (20%), Rock (20%)
- **Segment Length**: Variable lengths for variety
- **Shared Logic**: Same generation used for simulation and visual game

#### **Track Properties**
- **Total Length**: 1500 logical units
- **Visual Length**: 700 pixels on screen
- **Terrain Effects**: Different stat multipliers per terrain
- **Strategic Depth**: Turtle stats affect terrain performance

### 4.2 Race Mechanics

#### **Participant Setup**
- **Player Turtle**: Selected from active roster
- **Opponents**: 2 AI turtles (temporary if roster slots empty)
- **Equal Conditions**: All turtles follow same physics rules
- **No Direct Control**: Player watches, doesn't steer

#### **Race Progression**
- **Real-time Visualization**: Turtles move across screen
- **Speed Controls**: 1x, 2x, 4x time acceleration
- **Energy Management**: Turtles rest when exhausted
- **Finish Detection**: Automatic ranking when turtles finish

#### **Race Outcomes**
- **Ranking System**: 1st, 2nd, 3rd place determination
- **Reward Distribution**: Money based on finishing position
- **Betting Resolution**: Payouts calculated and awarded
- **Post-race Cleanup**: Energy restored, temporary turtles removed

### 4.3 Physics Implementation

#### **Movement Calculation**
```python
def update_physics(terrain_type):
    if resting:
        # Energy recovery
        energy += recovery * RECOVERY_RATE
        if energy >= threshold:
            resting = False
        return 0  # No movement while resting
    
    # Calculate movement speed
    speed = base_speed
    if terrain == "water":
        speed *= (swim / 10.0)
    elif terrain == "rock":
        speed *= (climb / 10.0)
    
    # Energy drain
    energy -= 0.5 * TERRAIN_DIFFICULTY
    if energy <= 0:
        energy = 0
        resting = True
    
    return speed
```

#### **Terrain Strategy**
- **Grass**: Relies on Speed stat
- **Water**: Requires high Swim skill
- **Rock**: Requires high Climb skill
- **Balanced Teams**: Diverse stats for varied terrain

---

## 5. Advanced Features

### 5.1 Profile System

#### **Turtle Information Display**
- **Detailed Stats**: All five stats with visual bars
- **Race History**: Last 5 races with positions and earnings
- **Energy Status**: Real-time energy for active turtles
- **Navigation**: Browse all turtles (active + retired)

#### **Data Tracking**
- **Race Results**: Automatic recording of position and earnings
- **Total Statistics**: Career races and earnings
- **Performance Metrics**: Historical race data
- **Visual Genetics**: Foundation for future image display

### 5.2 Visual Genetics Foundation

#### **Genetic Attributes**
- **Shell Colors**: Base, pattern, and accent RGB values
- **Shell Patterns**: 6 pattern types with density and size
- **Body Colors**: Base color and pattern types
- **Physical Traits**: Size, shape, and proportion factors

#### **Future Integration**
- **SVG Generation**: Procedural turtle image creation
- **Inheritance System**: Parent-to-child trait transmission
- **NEAT Evolution**: Advanced gene expression system
- **Rarity System**: Unique visual combination tracking

---

## 6. Game Balance

### 6.1 Progression Pacing

#### **Early Game**
- **Starting Resources**: $100, 1 starter turtle
- **Initial Challenges**: Limited roster, basic stats
- **Learning Curve**: Simple mechanics, clear objectives

#### **Mid Game**
- **Team Building**: Acquire complementary turtles
- **Breeding Strategy**: Balance current vs future potential
- **Economic Management**: Sustainable cash flow

#### **Late Game**
- **Optimization**: Perfect stat combinations
- **Advanced Breeding**: Multi-generational planning
- **Collection Building**: Rare trait combinations

### 6.2 Difficulty Balance

#### **Accessible Mechanics**
- **No Energy Cost for Training**: Reduces frustration
- **Forgiving Economy**: Multiple income sources
- **Clear Progression**: Visible improvement pathways

#### **Strategic Depth**
- **Sacrificial Choices**: Meaningful breeding decisions
- **Resource Management**: Limited roster slots
- **Risk vs Reward**: Betting system consequences

---

## 7. Quality of Life Features

### 7.1 User Experience

- **Mode-Aware Interfaces**: Different UI for different contexts
- **Visual Feedback**: Hover effects, selection highlights
- **Clear Navigation**: Header-based menu system
- **Error Prevention**: Actions only available when appropriate

### 7.2 Accessibility

- **Mouse-Driven**: Simple click interactions
- **Clear Labels**: Descriptive text for all actions
- **Intuitive Flow**: Logical progression through states
- **Forgiving Design**: No permanent mistakes

---

**This gameplay mechanics document provides the detailed rules and systems that make Turbo Shells engaging and strategically deep while remaining accessible to new players.** 🎮
