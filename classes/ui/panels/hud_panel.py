"""
hud_panel.py

Renders bottom hud panel for displaying
waves, question and guide buttons

Author(s): Braeden
Created: 2026-02-26
"""

import classes.constants as c
import pygame

from classes.ui.button import Button

class HudPanel:
    def __init__(self, game, get_font):
        self.game = game
        self.get_font = get_font

        self.start_wave = Button(None, "Start Wave", (c.SCREEN_WIDTH // 1.2, 950), get_font(64), "white", "grey")
        self.answer_questions = Button(None, "Questions", (c.SCREEN_WIDTH // 1.7, 950), get_font(64), "white", "grey")
        self.guide_button = Button(None, "Guide", (c.SCREEN_WIDTH // 2.7, 950), get_font(64), "white", "grey")

    def draw(self, mouse_pos):
        pygame.draw.rect(self.game.screen, "#445d68", (0, self.game.grid.grid_area_height, c.SCREEN_WIDTH, c.SCREEN_HEIGHT - self.game.grid.grid_area_height))

        energy_text = self.get_font(54).render(str(self.game.gameplay.energy_amount), True, "white")
        self.game.screen.blit(energy_text, (125, self.game.grid.grid_area_height + 25))
        self.game.screen.blit(self.game.assets.icons["energy"], (25, self.game.grid.grid_area_height + 20))

        research_text = self.get_font(54).render(str(self.game.gameplay.research_amount), True, "white")
        self.game.screen.blit(research_text, (125, self.game.grid.grid_area_height + 125))
        self.game.screen.blit(self.game.assets.icons["research"], (25, self.game.grid.grid_area_height + 120))

        if not self.game.antiparticle_group:
            self.start_wave.changeColor(mouse_pos)
            self.start_wave.update(self.game.screen)
        
        wave_text = self.get_font(32).render(f"Wave {self.game.gameplay.current_wave}/{self.game.gameplay.total_waves}", True, "white")
        wave_rect = wave_text.get_rect(center=(c.SCREEN_WIDTH // 1.1, 1020))
        self.game.screen.blit(wave_text, wave_rect)

        self.answer_questions.changeColor(mouse_pos)
        self.answer_questions.update(self.game.screen)

        self.guide_button.changeColor(mouse_pos)
        self.guide_button.update(self.game.screen)
