"""Pure positioning data for UI layouts."""

import pygame

# Padding
PADDING = 20

# 1. Global Header
HEADER_RECT = pygame.Rect(0, 0, 800, 40)
HEADER_TITLE_POS = (20, 10)
HEADER_MONEY_POS = (650, 10)

# 2. Roster Layout
SLOT_1_RECT = pygame.Rect(50, 60, 700, 120)
SLOT_2_RECT = pygame.Rect(50, 200, 700, 120)
SLOT_3_RECT = pygame.Rect(50, 340, 700, 120)
SLOT_RECTS = [SLOT_1_RECT, SLOT_2_RECT, SLOT_3_RECT]

# Inside Slot (Relative to Slot Rect)
SLOT_NAME_POS = (20, 10)
SLOT_STATS_POS = (20, 35)
SLOT_ENERGY_BG_RECT = pygame.Rect(20, 65, 400, 15)
SLOT_ENERGY_FILL_POS = (22, 67) # Width is variable, Height is 11
SLOT_BTN_TRAIN_RECT = pygame.Rect(550, 15, 80, 28)
SLOT_BTN_RETIRE_RECT = pygame.Rect(550, 48, 80, 28)

# View toggles
VIEW_ACTIVE_RECT = pygame.Rect(50, 480, 100, 35)
VIEW_RETIRED_RECT = pygame.Rect(160, 480, 100, 35)

# Betting buttons
BET_BTN_NONE_RECT = pygame.Rect(280, 480, 90, 35)
BET_BTN_5_RECT = pygame.Rect(380, 480, 90, 35)
BET_BTN_10_RECT = pygame.Rect(480, 480, 90, 35)

# 3. Main Menu Layout
MENU_ROSTER_RECT = pygame.Rect(200, 150, 400, 80)
MENU_SHOP_RECT = pygame.Rect(200, 250, 400, 80)
MENU_BREEDING_RECT = pygame.Rect(200, 350, 400, 80)
MENU_RACE_RECT = pygame.Rect(200, 450, 400, 80)

# 4. Shop Layout
SHOP_SLOT_1_RECT = pygame.Rect(50, 100, 200, 300)
SHOP_SLOT_2_RECT = pygame.Rect(300, 100, 200, 300)
SHOP_SLOT_3_RECT = pygame.Rect(550, 100, 200, 300)
SHOP_SLOT_RECTS = [SHOP_SLOT_1_RECT, SHOP_SLOT_2_RECT, SHOP_SLOT_3_RECT]

SHOP_BTN_BUY_RECT = pygame.Rect(20, 240, 160, 40)
SHOP_BTN_REFRESH_RECT = pygame.Rect(300, 450, 200, 50)
SHOP_BTN_BACK_RECT = pygame.Rect(300, 520, 200, 50)

# 5. Breeding Layout
BREED_BACK_BTN_RECT = pygame.Rect(300, 520, 200, 50)
BREED_BTN_RECT = pygame.Rect(300, 450, 200, 50)

# 6. Race Layout
LANE_1_RECT = pygame.Rect(0, 100, 800, 100)
LANE_2_RECT = pygame.Rect(0, 220, 800, 100)
LANE_3_RECT = pygame.Rect(0, 340, 800, 100)
