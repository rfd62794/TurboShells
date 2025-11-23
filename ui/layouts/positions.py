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
SLOT_BTN_TRAIN_RECT = pygame.Rect(540, 15, 90, 32)  # Larger and more to the left
SLOT_BTN_RETIRE_RECT = pygame.Rect(540, 52, 90, 32)  # Larger and more to the left

# View toggles
VIEW_ACTIVE_RECT = pygame.Rect(50, 480, 100, 35)
VIEW_RETIRED_RECT = pygame.Rect(160, 480, 100, 35)

# Betting buttons
BET_BTN_NONE_RECT = pygame.Rect(280, 480, 90, 35)
BET_BTN_5_RECT = pygame.Rect(380, 480, 90, 35)
BET_BTN_10_RECT = pygame.Rect(480, 480, 90, 35)

# 5. Profile View Layout (Image-Ready Design)
PROFILE_HEADER_RECT = pygame.Rect(0, 0, 800, 60)
PROFILE_TITLE_POS = (20, 20)
PROFILE_BACK_BTN_RECT = pygame.Rect(700, 15, 80, 30)

# Left Panel - Turtle Visual (future image area)
PROFILE_VISUAL_PANEL_RECT = pygame.Rect(50, 80, 300, 400)
PROFILE_TURTLE_IMAGE_POS = (200, 230)  # Center position for future turtle image
PROFILE_TURTLE_IMAGE_SIZE = (200, 200)  # Placeholder size for SVG/image

# Right Panel - Detailed Information
PROFILE_INFO_PANEL_RECT = pygame.Rect(370, 80, 380, 400)
PROFILE_TURTLE_NAME_POS = (390, 100)
PROFILE_TURTLE_STATUS_POS = (390, 130)
PROFILE_TURTLE_AGE_POS = (390, 160)

# Stats Section (right panel)
PROFILE_STATS_HEADER_POS = (390, 200)
PROFILE_STATS_START_Y = 230
PROFILE_STATS_HEIGHT = 25
PROFILE_STATS_BAR_WIDTH = 150
PROFILE_STATS_BAR_X = 530

# Energy Section (right panel)
PROFILE_ENERGY_HEADER_POS = (390, 360)
PROFILE_ENERGY_BAR_POS = (390, 390)
PROFILE_ENERGY_BG_RECT = pygame.Rect(390, 390, 300, 20)

# Bottom Section - Race History
PROFILE_HISTORY_PANEL_RECT = pygame.Rect(50, 500, 700, 80)
PROFILE_HISTORY_HEADER_POS = (70, 510)
PROFILE_HISTORY_START_Y = 535
PROFILE_HISTORY_HEIGHT = 18

# Navigation (bottom)
PROFILE_NAV_RECT = pygame.Rect(300, 580, 200, 15)
PROFILE_PREV_BTN_RECT = pygame.Rect(250, 575, 80, 25)
PROFILE_NEXT_BTN_RECT = pygame.Rect(470, 575, 80, 25)
PROFILE_DOTS_START_X = 340
PROFILE_DOTS_Y = 590

# 6. Main Menu Layout
MENU_ROSTER_RECT = pygame.Rect(200, 120, 400, 70)
MENU_SHOP_RECT = pygame.Rect(200, 210, 400, 70)
MENU_BREEDING_RECT = pygame.Rect(200, 300, 400, 70)
MENU_RACE_RECT = pygame.Rect(200, 390, 400, 70)
MENU_VOTING_RECT = pygame.Rect(200, 480, 400, 70)

# 4. Shop Layout - Redesigned for larger images and better layout
SHOP_SLOT_1_RECT = pygame.Rect(50, 80, 220, 380)  # Larger and extended down
SHOP_SLOT_2_RECT = pygame.Rect(290, 80, 220, 380)  # Larger and extended down  
SHOP_SLOT_3_RECT = pygame.Rect(530, 80, 220, 380)  # Larger and extended down
SHOP_SLOT_RECTS = [SHOP_SLOT_1_RECT, SHOP_SLOT_2_RECT, SHOP_SLOT_3_RECT]

# Inside Shop Slot (Relative to Slot Rect) - Adjusted for larger boxes
SHOP_SLOT_NAME_POS = (20, 15)
SHOP_SLOT_STATS_POS = (20, 45)  # Moved down
SHOP_SLOT_ENERGY_BG_RECT = pygame.Rect(20, 280, 180, 15)  # Moved down
SHOP_SLOT_ENERGY_FILL_POS = (22, 282)  # Moved down
SHOP_SLOT_BTN_BUY_RECT = pygame.Rect(20, 320, 180, 40)  # Moved down

# Bottom buttons - Refresh moved to bottom, back button in header
SHOP_BTN_REFRESH_RECT = pygame.Rect(300, 480, 200, 50)  # Moved to bottom

# 5. Breeding Layout
BREED_BACK_BTN_RECT = pygame.Rect(300, 520, 200, 50)
BREED_BTN_RECT = pygame.Rect(300, 450, 200, 50)

# 6. Race Layout
LANE_1_RECT = pygame.Rect(0, 100, 800, 100)
LANE_2_RECT = pygame.Rect(0, 220, 800, 100)
LANE_3_RECT = pygame.Rect(0, 340, 800, 100)
