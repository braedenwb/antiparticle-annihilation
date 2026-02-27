"""
guide_panel.py

Renders guide overlay panel

Author(s): Braeden
Created: 2026-02-26
"""

import classes.constants as c
import pygame

from classes.ui.button import Button
from data.guides import GUIDES, GUIDE_SEQUENCE

class GuidePanel:
    def __init__(self, game, get_font, draw_wrapped_text):
        self.game = game
        self.get_font = get_font
        self.draw_wrapped_text = draw_wrapped_text

        self.guide_cards = GUIDES
        self.guide_sequence = [key for key in GUIDE_SEQUENCE if key in self.guide_cards]
        self.guide_index = 0 if self.guide_sequence else -1
        self.active_guide_key = self.guide_sequence[0] if self.guide_sequence else None
        self.guide_rect = pygame.Rect(c.SCREEN_WIDTH // 2 - 360, c.SCREEN_HEIGHT // 2 - 240, 720, 480)
        self.guide_close_button = Button(None, "X", (self.guide_rect.right - 30, self.guide_rect.top + 30), get_font(36), "red", "darkred")
        self.guide_next_button = Button(None, "Next", (self.guide_rect.right - 110, self.guide_rect.bottom - 40), get_font(30), "white", "grey")
        self.guide_back_button = Button( None, "Back", (self.guide_rect.left + 110, self.guide_rect.bottom - 40), get_font(30), "white", "grey")

    def close_guide(self):
        self.guide_index = -1
        self.active_guide_key = None

    def restart_guide(self):
        if not self.guide_sequence:
            self.close_guide()
            return

        self.guide_index = 0
        self.active_guide_key = self.guide_sequence[0]

    def draw_feature_guide(self, mouse_pos):
        if self.game.state != c.GAMEPLAY or self.active_guide_key is None:
            return

        guide = self.guide_cards.get(self.active_guide_key)
        if not guide:
            return

        overlay = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.game.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.game.screen, "#2e3f46", self.guide_rect, border_radius=18)
        pygame.draw.rect(self.game.screen, "#445d68", self.guide_rect, 4, border_radius=18)

        title_text = self.get_font(52).render(guide["title"], True, "white")
        title_rect = title_text.get_rect(midtop=(self.guide_rect.centerx, self.guide_rect.top + 25))
        self.game.screen.blit(title_text, title_rect)

        image_group = guide.get("image_group")
        image_key = guide.get("image_key")
        image = None
        if image_group == "tiles":
            image = self.game.assets.tiles.get(image_key)
        elif image_group == "elements":
            image = self.game.assets.elements.get(image_key, {}).get("grid")
        elif image_group == "antiparticles":
            image = self.game.assets.antiparticles.get(image_key, {}).get("grid")

        if image is not None:
            preview = pygame.transform.smoothscale(image, (120, 120))
            preview_rect = preview.get_rect(center=(self.guide_rect.centerx, self.guide_rect.centery - 50))
            self.game.screen.blit(preview, preview_rect)
            desc_rect = pygame.Rect(self.guide_rect.left + 60, self.guide_rect.bottom - 200, self.guide_rect.width - 120, 110)
        else:
            desc_rect = pygame.Rect(self.guide_rect.left + 60, self.guide_rect.top + 110, self.guide_rect.width - 120, self.guide_rect.height - 180)
        self.draw_wrapped_text(self.game.screen, guide["description"], self.get_font(28), "white", desc_rect, 34)

        is_last = self.guide_index >= len(self.guide_sequence) - 1
        self.guide_next_button.set_text("Done" if is_last else "Next")
        self.guide_next_button.changeColor(mouse_pos)
        self.guide_next_button.update(self.game.screen)

        if self.guide_index > 0:
            self.guide_back_button.changeColor(mouse_pos)
            self.guide_back_button.update(self.game.screen)

        self.guide_close_button.changeColor(mouse_pos)
        self.guide_close_button.update(self.game.screen)

    def advance_guide(self):
        if not self.guide_sequence:
            self.close_guide()
            return

        if self.guide_index < 0:
            self.restart_guide()
            return

        if self.guide_index >= len(self.guide_sequence) - 1:
            self.close_guide()
            return

        self.guide_index += 1
        self.active_guide_key = self.guide_sequence[self.guide_index]

    def reverse_guide(self):
        if not self.guide_sequence:
            self.close_guide()
            return

        if self.guide_index <= 0:
            self.guide_index = 0
            self.active_guide_key = self.guide_sequence[0]
            return

        self.guide_index -= 1
        self.active_guide_key = self.guide_sequence[self.guide_index]
