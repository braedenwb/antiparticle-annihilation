"""
state_handler.py

Handles all state-based logic for UI button interactions,
including authentication, settings, and menu navigation

Author(s): Braeden
Created: 2026-01-22
"""

import classes.managers.authentication_manager as auth
import classes.constants as c 
from classes.ui.button import Button

def handle_button(self, button: Button) -> None:
    """
    Handles button interactions based on current game state.
    
    :param Button button: the button object that was pressed.
    """
    if self.state == c.MAIN_MENU:
        if button.text_input == "Play":
            self.state = c.GAMEPLAY
        elif button.text_input == "Settings":
            self.state = c.SETTINGS
        elif button.text_input == "Achievements":
            self.state = c.ACHIEVEMENTS
        elif button.text_input == "Quit":
            self.running = False
    elif self.state == c.DIFFICULTY_SELECT:
        if button.text_input == "<":
            self.state = c.MAIN_MENU
        elif button.text_input in ["Beginner", "Intermediate", "Chemist"]:
            self.state = c.LEVEL_SELECT
    elif self.state == c.LEVEL_SELECT:
        if button.text_input == "<":
            self.state = c.MAIN_MENU
        elif button.text_input == "Tutorial":
            self.state = c.GAMEPLAY
    elif self.state == c.SETTINGS:
        if button.text_input == "<":
            self.state = c.MAIN_MENU
        elif button.text_input == "Profiles":
            self.settings_state = "Profiles"
        elif button.text_input == "Audio":
            self.settings_state = "Audio"
        elif button.text_input == "Clear All Data":
            self.settings_state = "Clear All Data"
    elif self.state == c.ACHIEVEMENTS:
        if button.text_input == "<":
            self.state = c.MAIN_MENU
    elif self.state == c.LOGIN:
        if button.text_input == "Log In":
            auth.handle_login(self)
        elif button.text_input == "Sign Up":
            self.state = c.SIGNUP
    elif self.state == c.SIGNUP:
        if button.text_input == "Create Account":
            auth.handle_signup(self)
        elif button.text_input == "Back to Login":
            self.state = c.LOGIN