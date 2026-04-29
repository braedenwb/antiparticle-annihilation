"""
constants.py

File for storing constant values used throughout the game.
Contains display config, timing config, UI layout values, and game state identifiers.

All constants are uppercase.
"""

# =========================
# Display Configuration
# =========================

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# =========================
# File Paths
# =========================

DB_PATH = "data/database/AcagameicsDatabase.db"

# =========================
# UI Layout
# =========================

UI_BOX_X = SCREEN_WIDTH // 36
UI_BOX_Y = SCREEN_HEIGHT // 1.25

PANEL_X = 30
PANEL_Y = 500
PANEL_W = 240
PANEL_H = 260

# =========================
# Game States
# =========================

MAIN_MENU = "main_menu"
GAMEPLAY = "gameplay"
DIFFICULTY_SELECT = "difficulty_select"
LEVEL_SELECT = "level_select"
LEVEL_BRIEFING = "level_briefing"
SETTINGS = "settings"
ACHIEVEMENTS = "achievements"
LOGIN = "log_in"
SIGNUP = "sign_up"
QUESTIONS = "questions"
ELEMENT_SHOP = "element_shop"
