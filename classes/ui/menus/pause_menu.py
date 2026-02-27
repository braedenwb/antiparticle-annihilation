"""
pause_menu.py

Renders and sets up pause menu during gameplay

Author(s): Braeden
Created: 2026-02-26
"""

import classes.constants as c
import pygame

from classes.ui.button import Button

class PauseMenu:
    def __init__(self, game, get_font):
        self.game = game
        self.get_font = get_font

        self.box_rect = pygame.Rect(c.SCREEN_WIDTH // 2 - 300, c.SCREEN_HEIGHT // 2 - 150, 600, 300)

        self.yes_button = Button(None, "Yes", (self.box_rect.centerx - 100, self.box_rect.bottom - 60), get_font(28), "white", "grey")
        self.cancel_button = Button(None, "Cancel", (self.box_rect.centerx + 100, self.box_rect.bottom - 60), get_font(28), "white", "grey")

        self.pause_overlay = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.pause_overlay.set_alpha(180)
        self.pause_overlay.fill((0, 0, 0))

    def draw(self, mouse_pos):
        if not self.game.paused:
            return

        self.game.screen.blit(self.pause_overlay, (0, 0))

        pygame.draw.rect(self.game.screen, "#2e3f46", self.box_rect, border_radius=15)
        pygame.draw.rect(self.game.screen, "#445d68", self.box_rect, 4, border_radius=15)

        if self.game.gameplay.lose:
            title = self.get_font(50).render("You lost!", True, "white")
        elif self.game.gameplay.win:
            title = self.get_font(40).render("You finished the tutorial!", True, "white")
        else:
            title = self.get_font(36).render("Leave the game?", True, "white")
            text = self.get_font(24).render("All progress will be lost.", True, "white")
            text_rect = text.get_rect(center=(self.box_rect.centerx, self.box_rect.centery - 10))
            self.game.screen.blit(text, text_rect)

            self.yes_button.changeColor(mouse_pos)
            self.cancel_button.changeColor(mouse_pos)
            self.yes_button.update(self.game.screen)
            self.cancel_button.update(self.game.screen)

        title_rect = title.get_rect(center=(self.box_rect.centerx, self.box_rect.top + 100))
        self.game.screen.blit(title, title_rect)