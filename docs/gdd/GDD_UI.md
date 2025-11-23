# Game Design Document: Turbo Shells - UI Specification

**Version:** 1.1 (Enhanced MVP)  
**Date:** November 22, 2025  
**Focus:** User interface design and screen specifications

---

## 1. UI Architecture Overview

### 1.1 Design Philosophy

- **Component-Based**: Reusable UI elements throughout all screens
- **Mode-Aware**: Different interfaces based on game context
- **Clean Navigation**: Header-based menu system with clear back buttons
- **Visual Feedback**: Hover effects, selection highlights, status indicators

### 1.2 Layout System

#### **Position Management**
- **Centralized Layout**: All positioning data in `ui/layouts/positions.py`
- **Absolute Positioning**: Consistent pixel-perfect placement
- **Component Reuse**: Shared positioning across similar elements
- **Responsive Design**: 800x600 fixed resolution with optimized layouts

#### **Visual Components**
- **Button Class**: Standardized button with hover states
- **TurtleCard Class**: Reusable turtle display component
- **Layout Constants**: Named positions for maintainability

---

## 2. Screen Specifications

### 2.1 Main Menu (STATE_MENU)

**View:** `ui/menu_view.py`  
**Manager:** `StateHandler`

#### **Layout**
- **Header**: "TURBO SHELLS" title
- **Menu Options**: 4 large buttons (200x80px each)
  - ROSTER - Manage turtles
  - SHOP - Buy new turtles  
  - BREEDING - Breed turtles
  - RACE - Start race (via select racer mode)

#### **Visual Design**
- **Background**: Dark theme with accent colors
- **Buttons**: Hover effects, clear labeling
- **Navigation**: Clean, centered layout
- **Status**: Game state indicators (money, etc.)

#### **Interactions**
- **Mouse Click**: Select menu option
- **Hover Effects**: Visual feedback on button hover
- **State Transitions**: Smooth transitions to selected screens

---

### 2.2 Stable / Roster Management (STATE_ROSTER)

**View:** `ui/roster_view.py`  
**Manager:** `RosterManager`

#### **Layout Structure**
- **Header**: Dynamic title ("STABLE" or "SELECT RACER")
- **Menu Button**: Return to main menu
- **Turtle Slots**: 3 vertical slots (200x300px each)
- **View Toggle**: Active/Retired roster switch
- **Betting Controls**: $0/$5/$10 bet buttons (select racer mode only)

#### **Turtle Card Display**
Each slot shows:
- **Name**: Large, prominent text
- **Status Tag**: [ACTIVE] or [RETIRED]
- **Age**: Current age in days
- **Stats Summary**: Speed, Energy, Recovery, Swim, Climb
- **Energy Bar**: Visual energy indicator (active turtles only)
- **Action Buttons**: TRAIN, REST, RETIRE (active turtles only)

#### **Mode-Aware Interfaces**

**Normal Mode:**
- **Header**: "STABLE"
- **Actions**: Train, Rest, Retire buttons
- **Navigation**: View toggle between Active/Retired

**Select Racer Mode:**
- **Header**: "SELECT RACER"
- **Betting**: Bet amount selection
- **Simplified**: No train/retire buttons
- **Focus**: Turtle selection for racing

#### **Visual Feedback**
- **Selection Highlight**: Current turtle emphasized
- **Hover Effects**: Interactive elements respond to mouse
- **Status Colors**: Green (active), Yellow (retired), Gray (empty)
- **Energy Visualization**: Real-time energy bars

---

### 2.3 Race View (STATE_RACE)

**View:** `ui/race_view.py`  
**Manager:** `RaceManager`

#### **Layout**
- **Race Track**: 700px wide visual track
- **Turtle Lanes**: 3 horizontal lanes (player + 2 opponents)
- **Terrain Visualization**: Color-coded track segments
- **Finish Line**: Clear end point indicator
- **Speed Controls**: 1x, 2x, 4x speed buttons

#### **Visual Elements**
- **Turtle Sprites**: Colored rectangles representing turtles
- **Energy Bars**: Above each turtle showing current energy
- **Terrain Segments**: Grass (green), Water (blue), Rock (gray)
- **Progress Indicators**: Visual race progress

#### **Real-time Information**
- **Speed Multiplier**: Current race speed display
- **Bet Amount**: Current bet (if placed)
- **Race Progress**: Distance completed indicator
- **Energy Status**: Resting vs running states

#### **Interactions**
- **Speed Controls**: Adjust race speed (1x, 2x, 4x)
- **Visual Feedback**: Energy state changes (resting colors)
- **Automatic Progression**: Race continues without user input

---

### 2.4 Race Results (STATE_RACE_RESULT)

**View:** `ui/race_view.py` (results section)  
**Manager:** `RaceManager`

#### **Layout**
- **Results List**: Finish order with turtle details
- **Player Highlight**: User's turtle emphasized
- **Reward Summary**: Position and earnings display
- **Action Buttons**: MENU, RACE AGAIN options

#### **Information Display**
For each finisher:
- **Rank**: 1st, 2nd, 3rd position
- **Name**: Turtle identifier
- **Status**: Active/Retired indicator
- **Age**: Current age

#### **Reward Information**
- **Position**: User's finishing position
- **Base Reward**: Race prize money
- **Bet Payout**: Betting winnings (if applicable)
- **Total Earnings**: Combined income

#### **Navigation Options**
- **MENU**: Return to main menu
- **RACE AGAIN**: Start new race with same setup
- **Auto-Cleanup**: Temporary opponents removed

---

### 2.5 Shop (STATE_SHOP)

**View:** `ui/shop_view.py`  
**Manager:** `ShopManager`

#### **Layout**
- **Header**: "TURTLE SHOP" title
- **Inventory**: 3 turtle cards (200x300px each)
- **Shop Controls**: REFRESH button, MENU button
- **Money Display**: Current funds shown

#### **Turtle Shop Cards**
Each card displays:
- **Name**: Generated turtle name
- **Stats Summary**: All five core stats
- **Price**: Dynamic pricing based on stats
- **BUY Button**: Purchase option (if affordable)
- **Visual Feedback**: Hover effects, affordability indicators

#### **Shop Mechanics**
- **Initial Stock**: 3 random turtles (free on first load)
- **Refresh Cost**: $5 to regenerate inventory
- **Dynamic Pricing**: Higher stats = higher prices
- **Purchase Validation**: Check roster space and funds

#### **Visual Design**
- **Product Layout**: Clean, card-based display
- **Price Indicators**: Clear cost display
- **Affordability**: Visual feedback for purchasable turtles
- **Status Messages**: Shop feedback and notifications

---

### 2.6 Breeding Center (STATE_BREEDING)

**View:** `ui/breeding_view.py`  
**Manager:** `BreedingManager`

#### **Layout**
- **Header**: "BREEDING CENTER" title
- **Parent Selection**: Combined list of all turtles
- **Selection Display**: Parent A and Parent B indicators
- **Breed Controls**: BREED button, MENU button

#### **Turtle Selection**
- **Combined Roster**: Active + Retired turtles
- **Selection State**: Visual indication of chosen parents
- **Max Selection**: Limit to 2 parents
- **Clear Labels**: Parent A, Parent B indicators

#### **Breeding Interface**
- **Parent Display**: Selected parents shown prominently
- **Breed Button**: Active only when 2 parents selected
- **Space Check**: Validates roster availability
- **Preview**: Future enhancement for offspring preview

#### **Visual Feedback**
- **Selection Highlights**: Chosen parents emphasized
- **Validation Messages**: Clear feedback on breeding eligibility
- **Status Indicators**: Breeding progress and results

---

### 2.7 Profile View (STATE_PROFILE) ✅ NEW

**View:** `ui/views/profile_view.py`  
**Manager:** `StateHandler`

#### **Image-Ready Layout**
- **Header**: "TURTLE PROFILE" with MENU button
- **Left Panel**: Turtle visual area (300x400px) - future image display
- **Right Panel**: Detailed information (380x400px)
- **Bottom Section**: Race history (700x80px)
- **Navigation**: Previous/Next arrows with dots indicator

#### **Left Panel - Visual Display**
- **Image Area**: 200x200px placeholder for future turtle images
- **Visual Genetics**: Foundation for shell/color display
- **Centered Design**: Prominent visual presentation
- **Future Ready**: SVG integration planned

#### **Right Panel - Information**
- **Turtle Name**: Large, prominent display (28pt font)
- **Status**: [ACTIVE] or [RETIRED] with color coding
- **Age**: Current age display
- **Detailed Stats**: All five stats with visual bars
- **Energy Status**: Real-time energy for active turtles

#### **Stats Display**
Each stat shows:
- **Name**: Stat label (Speed, Max Energy, etc.)
- **Value**: Current stat number
- **Visual Bar**: Scaled visual representation
- **Descriptions**: Brief stat purpose explanation

#### **Race History Section**
- **Header**: "RACE HISTORY (Last 5)"
- **Race List**: Position, earnings, race number
- **Compact Display**: Efficient use of space
- **Historical Data**: Career performance tracking

#### **Navigation System**
- **Arrow Buttons**: ← PREV / NEXT → controls
- **Navigation Dots**: Visual position indicators
- **Full Collection**: Browse all turtles (active + retired)
- **Smooth Transitions**: Quick navigation between turtles

---

## 3. Component System

### 3.1 Button Component

**File:** `ui/components/button.py`

#### **Features**
- **Reusable**: Standardized button across all screens
- **Hover Effects**: Visual feedback on mouse hover
- **Customizable**: Text, colors, sizes
- **Consistent**: Uniform behavior throughout game

#### **Usage**
```python
button = Button(rect, text, base_color, hover_color)
button.draw(screen, mouse_pos)
if button.is_clicked(pos):
    # Handle click
```

### 3.2 TurtleCard Component

**File:** `ui/components/turtle_card.py`

#### **Features**
- **Unified Display**: Consistent turtle presentation
- **Dynamic Content**: Adapts to turtle state
- **Interactive Elements**: Click detection for actions
- **Visual States**: Active, retired, empty slot indicators

#### **Display Elements**
- **Turtle Information**: Name, stats, age, status
- **Energy Bar**: Real-time energy visualization
- **Action Buttons**: Context-sensitive controls
- **Selection States**: Visual feedback for selection

---

## 4. Layout System

### 4.1 Position Management

**File:** `ui/layouts/positions.py`

#### **Screen Layouts**
- **Main Menu**: Centered button layout
- **Roster**: 3-slot vertical arrangement
- **Shop**: 3-card horizontal layout
- **Race**: Track visualization with lanes
- **Profile**: Image-ready dual-panel design

#### **Component Positioning**
- **Named Constants**: Descriptive position names
- **Absolute Coordinates**: Pixel-perfect placement
- **Reusable Elements**: Shared positioning across screens
- **Maintenance Friendly**: Centralized layout management

### 4.2 Visual Hierarchy

#### **Information Priority**
1. **Primary**: Headers, current turtle, important actions
2. **Secondary**: Stats, navigation, secondary information
3. **Tertiary**: History, details, supplementary data

#### **Visual Weight**
- **Size**: Larger elements for importance
- **Color**: Bright colors for active elements
- **Position**: Top/left for primary information
- **Contrast**: High contrast for readability

---

## 5. User Experience Design

### 5.1 Interaction Patterns

#### **Click Interactions**
- **Primary Actions**: Left-click for all interactions
- **Hover Feedback**: Visual response to mouse position
- **Click Validation**: Actions only when appropriate
- **Error Prevention**: Disable invalid actions

#### **Navigation Flow**
- **Linear Progression**: Logical screen transitions
- **Quick Access**: Header buttons for main navigation
- **Contextual Back**: Return to previous screen
- **Mode Awareness**: Different interfaces for different contexts

### 5.2 Visual Feedback

#### **State Indicators**
- **Selection**: Highlighted borders, color changes
- **Hover Effects**: Brightening, border emphasis
- **Status Colors**: Green (active), Yellow (retired), Gray (inactive)
- **Energy States**: Color-coded energy bars

#### **Information Display**
- **Clear Labels**: Descriptive text for all elements
- **Consistent Formatting**: Uniform text presentation
- **Progress Indicators**: Visual bars, dots, meters
- **Status Messages**: Clear feedback for user actions

---

## 6. Accessibility & Usability

### 6.1 Accessibility Features

- **Mouse-Only Interface**: No keyboard requirements
- **Clear Visual Hierarchy**: Important elements emphasized
- **High Contrast**: Readable text and clear boundaries
- **Large Click Targets**: Easy to interact with buttons

### 6.2 Usability Principles

- **Consistency**: Same elements behave same way everywhere
- **Predictability**: Users can anticipate interface behavior
- **Feedback**: Every action provides clear response
- **Recovery**: Easy to undo or return from mistakes

---

## 7. Future UI Enhancements

### 7.1 Planned Improvements

- **Animations**: Smooth transitions between states
- **Sound Effects**: Audio feedback for interactions
- **Visual Polish**: Enhanced graphics and effects
- **Tooltips**: Additional information on hover

### 7.2 Advanced Features

- **Customization**: User preferences for interface
- **Themes**: Alternative color schemes
- **Responsive Design**: Adaptive to different resolutions
- **Accessibility Options**: High contrast modes, larger text

---

**This UI specification provides the complete design blueprint for Turbo Shells' user interface, ensuring consistency, usability, and visual appeal across all game screens.** 🎨
