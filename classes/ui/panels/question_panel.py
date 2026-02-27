"""
Author: Kelsey Cole 
Created: 1/22/2026
Summary: This class is the core component for the questions module, 
when the "Questions" button is pressed from the main gameplay loop.
"""

import classes.constants as c 
import pygame 

from classes.ui.button import Button
from classes.ui.game_error import GameError
from classes.ui.menus.menu_setup import MenuSetup

def get_font(size):
    return pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", size)

class QuestionPanel:
    def __init__(self, screen):
        self.state = c.QUESTIONS
        self.screen = screen        
        self.get_font = get_font
        self.screen.fill("black")
        self.main_volume_slider = None

        self.active_error = None
        self.error_start_time = None
        
    
    ## This method (should) create the 4 boxes that the user can click on 
    def draw_question_boxes(self, mouse_pos): #ADDED 
        self.screen.fill("black")

        question = MenuSetup(200, None, "What is at the center of an atom?", None, self.get_font(72), None, "white")
        back_button = Button(None, "<", (200, 200), self.get_font(200), "darkred", "red")

        quest1 = Button(None, "Nucleus", (c.SCREEN_WIDTH // 3, c.SCREEN_HEIGHT // 2.5), self.get_font(72), "white", "grey")
        quest2 = Button(None, "Electrons", (c.SCREEN_WIDTH // 1.5, c.SCREEN_HEIGHT // 2.5), self.get_font(72), "white", "grey")
        quest3 = Button(None, "A ball", (c.SCREEN_WIDTH // 3, c.SCREEN_HEIGHT // 1.5), self.get_font(72), "white", "grey")
        quest4 = Button(None, "Gas", (c.SCREEN_WIDTH // 1.5, c.SCREEN_HEIGHT // 1.5), self.get_font(72), "white", "grey")

        buttons = [back_button, quest1, quest2, quest3, quest4]

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        self.screen.blit(question.title_text, question.title_text_rect)

        return buttons

    def wrong_answer(self):
        self.active_error = GameError("Wrong answer!")
        self.error_start_time = pygame.time.get_ticks()

    def correct_answer(self):
        self.active_error = GameError("Correct!")
        self.error_start_time = pygame.time.get_ticks()
