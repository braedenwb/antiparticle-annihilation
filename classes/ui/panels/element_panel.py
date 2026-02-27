"""
element_panel.py

Renders element upgrade / buy panel
on side of screen

Author(s): Braeden
Created: 2026-02-26
"""

import pygame

from classes.ui.button import Button
from data.element_data import ELEMENT_DATA 

class ElementPanel:
    def __init__(self, game, get_font, draw_centered_wrapped_text):
        self.game = game
        self.get_font = get_font
        self.draw_centered_wrapped_text = draw_centered_wrapped_text

        self.PANEL_X = self.game.grid.side_margin // 3
        self.PANEL_Y = 25

        self.hydrogen_select = Button(self.game.assets.elements["hydrogen"]["button"], "", (self.game.grid.side_margin // 6, 75), get_font(32), "white", "grey")
        self.oxygen_select = Button(self.game.assets.elements["oxygen"]["button"], "", (self.game.grid.side_margin // 6, 200), get_font(32), "white", "grey")
        self.silicon_select = Button(self.game.assets.elements["silicon"]["button"], "", (self.game.grid.side_margin // 6, 350), get_font(32), "white", "grey")

        self.upgrade_exit_button = Button(None, "X", (self.PANEL_X + 275, self.PANEL_Y + 25), get_font(28), "red", "darkred")
        self.upgrade_button = Button(None, "", (self.PANEL_X + 150, self.PANEL_Y + 90), get_font(26), "white", "grey")

        self.buy_exit_button = Button(None, "X", (self.PANEL_X + 275, self.PANEL_Y + 25), get_font(28), "red", "darkred")
        self.buy_button = Button(None, f"", (self.PANEL_X + 150, self.PANEL_Y + 90), get_font(26), "white", "grey")

    def draw(self, mouse_pos):
        screen = self.game.screen
        grid = self.game.grid
        LINE_HEIGHT = self.game.LINE_HEIGHT

        for button in [self.hydrogen_select, self.oxygen_select, self.silicon_select]:
            button.update(screen)

        # Determine which panel to draw
        element_obj = self.game.selected_element_obj
        element_name = self.game.selected_element_button

        if element_obj:
            data = ELEMENT_DATA.get(element_obj.name, {})
            title = element_obj.name.capitalize()
            upgrade_cost = element_obj.upgrade_cost
        elif element_name:
            data = ELEMENT_DATA.get(element_name, {})
            title = element_name.capitalize()
            upgrade_cost = data.get("buy_cost", 0)
        else:
            return  # nothing selected

        # Draw panel background
        panel_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, 300, grid.grid_area_height - 50)
        pygame.draw.rect(screen, "#405761", panel_rect, border_radius=15)
        pygame.draw.rect(screen, "#2e3f46", panel_rect, 4, border_radius=15)

        # Draw title
        title_text = self.get_font(28).render(title, True, "white")
        title_rect = title_text.get_rect(center=(self.PANEL_X + 150, 45))
        screen.blit(title_text, title_rect)

        # Draw buttons
        if element_obj:
            self.upgrade_exit_button.changeColor(mouse_pos)
            self.upgrade_exit_button.update(screen)

            self.upgrade_button.set_text(f"Upgrade for {upgrade_cost}")
            self.upgrade_button.changeColor(mouse_pos)
            self.upgrade_button.update(screen)
        else:
            self.buy_exit_button.changeColor(mouse_pos)
            self.buy_exit_button.update(screen)

            self.buy_button.set_text(f"Buy for {upgrade_cost}")
            self.buy_button.changeColor(mouse_pos)
            self.buy_button.update(screen)

        # Draw element info
        text_rect = pygame.Rect(self.PANEL_X + 25, self.PANEL_Y + 160, 250, grid.grid_area_height - 180)
        if data.get('damage_element'):
            info_lines = [
                f"Level: {getattr(element_obj, 'upgrade_level', '-')}",
                f"HP: {data['hp']}",
                f"Damage: {getattr(element_obj, 'damage', data.get('damage', 0))}",
                f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                f"State: {data['state']}",
                data['desc']
            ]
        elif data.get('healing_element'):
            info_lines = [
                f"Level: {getattr(element_obj, 'upgrade_level', '-')}",
                f"HP: {data['hp']}",
                f"Healing: {data['healing']}",
                f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                f"State: {data['state']}",
                data['desc']
            ]
        elif data.get('energy_element'):
            info_lines = [
                f"Level: {getattr(element_obj, 'upgrade_level', '-')}",
                f"HP: {data['hp']}",
                f"Energy: {data['energy_generation']}",
                f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                f"State: {data['state']}",
                data['desc']
            ]
        else:
            info_lines = []

        y_offset = text_rect.top
        for line in info_lines:
            self.draw_centered_wrapped_text(
                screen,
                line,
                self.get_font(24),
                "white",
                pygame.Rect(text_rect.left, y_offset, text_rect.width, 60),
                LINE_HEIGHT
            )
            y_offset += 40