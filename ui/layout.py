import pygame

# Padding
PADDING = 20

# 1. Global Header
HEADER_RECT = pygame.Rect(0, 0, 800, 60)
HEADER_TITLE_POS = (20, 15)
HEADER_MONEY_POS = (650, 15)

# 2. Main Menu (The Stable)
# Roster Slots
SLOT_1_RECT = pygame.Rect(50, 80, 700, 120)
SLOT_2_RECT = pygame.Rect(50, 220, 700, 120)
SLOT_3_RECT = pygame.Rect(50, 360, 700, 120)
SLOT_RECTS = [SLOT_1_RECT, SLOT_2_RECT, SLOT_3_RECT]

# Inside Slot (Relative to Slot Rect)
SLOT_NAME_POS = (20, 10)
SLOT_STATS_POS = (20, 35)
SLOT_ENERGY_BG_RECT = pygame.Rect(20, 65, 400, 15)
SLOT_ENERGY_FILL_POS = (22, 67) # Width is variable, Height is 11
SLOT_BTN_TRAIN_RECT = pygame.Rect(550, 15, 80, 28)
SLOT_BTN_RETIRE_RECT = pygame.Rect(550, 48, 80, 28)

# View toggles (Active vs Retired) on Stable
VIEW_ACTIVE_RECT = pygame.Rect(50, 440, 100, 35)
VIEW_RETIRED_RECT = pygame.Rect(160, 440, 100, 35)

# Stable Betting Buttons (MVP)
BET_BTN_NONE_RECT = pygame.Rect(280, 440, 90, 35)
BET_BTN_5_RECT = pygame.Rect(380, 440, 90, 35)
BET_BTN_10_RECT = pygame.Rect(480, 440, 90, 35)

# Bottom Navigation
NAV_MENU_RECT = pygame.Rect(300, 500, 200, 60)
NAV_SHOP_RECT = pygame.Rect(50, 500, 200, 60)
NAV_BREED_RECT = pygame.Rect(550, 500, 200, 60)

# 3. The Race Screen
LANE_1_RECT = pygame.Rect(0, 100, 800, 100)
LANE_2_RECT = pygame.Rect(0, 220, 800, 100)
LANE_3_RECT = pygame.Rect(0, 340, 800, 100)
LANE_RECTS = [LANE_1_RECT, LANE_2_RECT, LANE_3_RECT]

RACE_HUD_RECT = pygame.Rect(0, 480, 800, 120)
SPEED_1X_RECT = pygame.Rect(300, 520, 50, 40)
SPEED_2X_RECT = pygame.Rect(360, 520, 50, 40)
SPEED_4X_RECT = pygame.Rect(420, 520, 50, 40)
PROGRESS_BAR_RECT = pygame.Rect(50, 570, 700, 10)

# Race Result Screen buttons
RACE_RESULT_MENU_BTN_RECT = pygame.Rect(300, 450, 200, 50)
RACE_RESULT_RERUN_BTN_RECT = pygame.Rect(300, 520, 200, 50)

# 4. The Shop Screen
SHOP_SLOT_1_RECT = pygame.Rect(50, 100, 200, 300)
SHOP_SLOT_2_RECT = pygame.Rect(300, 100, 200, 300)
SHOP_SLOT_3_RECT = pygame.Rect(550, 100, 200, 300)
SHOP_SLOT_RECTS = [SHOP_SLOT_1_RECT, SHOP_SLOT_2_RECT, SHOP_SLOT_3_RECT]

# Inside Shop Slot (Relative)
SHOP_ICON_POS = (100, 50)
SHOP_STATS_POS = (20, 150)
SHOP_BTN_BUY_RECT = pygame.Rect(20, 240, 160, 40)

# Shop Controls
SHOP_BTN_REFRESH_RECT = pygame.Rect(300, 450, 200, 50)
SHOP_BTN_BACK_RECT = pygame.Rect(300, 520, 200, 50)

# 5. Breeding Screen (Custom addition based on need)
BREEDING_LIST_START_Y = 120
BREEDING_SLOT_HEIGHT = 60
BREEDING_ROW_X = 50
BREEDING_ROW_WIDTH = 600
BREED_BTN_RECT = pygame.Rect(300, 450, 200, 50)
BREED_BACK_BTN_RECT = pygame.Rect(300, 520, 200, 50)
