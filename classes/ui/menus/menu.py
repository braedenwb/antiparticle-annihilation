"""
    This class is for hosting all the menus 
    in the game: the main menu, the difficulty select menu,
    the level select menu, and more as the game grows
"""

import classes.constants as c
import classes.ui.text.text_utils as text
import math
import pygame
import pygame_widgets

from classes.ui.button import Button
from classes.ui.menus.menu_setup import MenuSetup
from classes.ui.text.textinput import TextInput 
from pygame_widgets.slider import Slider

class Menu:
    def __init__(self, screen, get_font, research_icon):
        self.screen = screen
        self.get_font = get_font
        self.research_icon = research_icon
        self.main_volume_slider = None
        self.level_maps = [
            {"id": "tutorial", "name": "Tutorial", "subtitle": "Welcome to Antiparticle Annihilation"},
            {"id": "map1", "name": "Placeholder 1", "subtitle": "Description"},
            {"id": "map2", "name": "Placeholder 2", "subtitle": "Description"},
            {"id": "map3", "name": "Placeholder 3", "subtitle": "Description"},
        ]
        self.username_input = TextInput(c.SCREEN_WIDTH // 2 - 150, c.SCREEN_HEIGHT // 2 - 50, 300, 60, text.get_font(40), placeholder="Username")
        self.password_input = TextInput(c.SCREEN_WIDTH // 2 - 150,c.SCREEN_HEIGHT // 2 + 50, 300, 60, text.get_font(40), placeholder="Password", password=True)

    def draw_main_menu(self, mouse_pos, username):
        self.screen.fill("black")

        pygame.draw.rect(
            self.screen, "snow2",
            (c.SCREEN_WIDTH // 6, c.SCREEN_HEIGHT // 10, c.SCREEN_WIDTH // 1.5, c.SCREEN_HEIGHT // 1.35),
            border_radius=20
        )

        menu_title = self.get_font(86).render("Antiparticle Annihilation", True, "black")
        menu_title_rect = menu_title.get_rect(center=(c.SCREEN_WIDTH // 2, 200))

        self.screen.blit(menu_title, menu_title_rect)

        current_profile = self.get_font(24).render("Logged in as: " + username, True, "white")
        
        self.screen.blit(current_profile, (0,0))

        buttons = [
            Button(None, "Play", (c.SCREEN_WIDTH // 2, 400), self.get_font(64), "black", "darkgrey"),
            Button(None, "Settings", (c.SCREEN_WIDTH // 2, 500), self.get_font(64), "black", "darkgrey"),
            Button(None, "Achievements", (c.SCREEN_WIDTH // 2, 600), self.get_font(64), "black", "darkgrey"),
            Button(None, "Quit", (c.SCREEN_WIDTH // 2, 700), self.get_font(64), "darkred", "red")
        ]

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return buttons

    # Difficulty selection menu
    def draw_difficulty_select(self, mouse_pos):
        self.screen.fill("black")

        title = MenuSetup(200, 300, "Select Difficulty", "Choose your difficulty", self.get_font(86), self.get_font(30), "white")

        back_button = Button(None, "<", (200, 200), self.get_font(200), "darkred", "red")
        
        box_width = c.SCREEN_WIDTH // 5
        box_height = c.SCREEN_HEIGHT // 2
        box_y = c.SCREEN_HEIGHT // 2.65
        spacing = 100

        total_width = 3 * box_width + 2 * spacing
        start_x = (c.SCREEN_WIDTH - total_width) // 2 

        colors = ["chartreuse3", "yellow1", "red"]
        labels = ["Beginner", "Intermediate", "Chemist"]
        fonts = [self.get_font(60), self.get_font(45), self.get_font(60)]
        desc_texts = [
            ("Easy questions.", "ghostwhite"),
            ("Moderate questions.", "black"),
            ("Hard questions.", "ghostwhite")
        ]

        buttons = [back_button]

        for i, (color, label, font, desc_info) in enumerate(zip(colors, labels, fonts, desc_texts)):
            x = start_x + i * (box_width + spacing)
            box_rect = pygame.Rect(x, box_y, box_width, box_height)
            pygame.draw.rect(self.screen, color, box_rect, 0, border_radius=20)

            button_y = box_rect.top + box_height * 0.15
            button_center = (box_rect.centerx, button_y)
            button = Button(None, label, button_center, font, "black", "grey57")
            button.update(self.screen)
            buttons.append(button)

            desc_text, desc_color = desc_info
            desc_surface = self.get_font(30).render(desc_text, True, desc_color)
            desc_rect = desc_surface.get_rect(center=(box_rect.centerx, button_y + 80))
            self.screen.blit(desc_surface, desc_rect)

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        self.screen.blit(title.title_text, title.title_text_rect)
        self.screen.blit(title.desc_text, title.desc_text_rect)
        
        return buttons

    def draw_level_select(self, mouse_pos, map_progress=None):
        self.screen.fill("black")

        title = MenuSetup(200, None, "Select Level", None, self.get_font(86), None, "white")
        back_button = Button(None, "<", (200, 200), self.get_font(200), "darkred", "red")
        buttons = [back_button]

        if map_progress is None:
            map_progress = {}

        columns = min(2, max(1, len(self.level_maps)))
        rows = max(1, math.ceil(len(self.level_maps) / columns))
        spacing_x = 45
        spacing_y = 35
        card_width = 560
        card_height = 250

        total_width = columns * card_width + (columns - 1) * spacing_x
        total_height = rows * card_height + (rows - 1) * spacing_y

        start_x = (c.SCREEN_WIDTH - total_width) // 2
        start_y = (c.SCREEN_HEIGHT - total_height) // 2 + 60

        for i, level in enumerate(self.level_maps):
            row = i // columns
            col = i % columns
            card_x = start_x + col * (card_width + spacing_x)
            card_y = start_y + row * (card_height + spacing_y)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            hover = card_rect.collidepoint(mouse_pos)

            is_completed = bool(map_progress.get(level["id"], False))
            status_text = "Completed" if is_completed else "Not Completed"
            status_color = "chartreuse3" if is_completed else "tomato2"
            card_color = "#4c6f7b" if hover else "#3a5360"

            pygame.draw.rect(self.screen, card_color, card_rect, border_radius=16)
            pygame.draw.rect(self.screen, "#24363e", card_rect, 4, border_radius=16)

            name_button_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            name_button = Button(
                name_button_surface,
                level["name"],
                (card_rect.centerx, card_rect.centery - 50),
                self.get_font(54),
                "white",
                "white"
            )
            name_button.map_id = level["id"]
            buttons.append(name_button)
            name_button.update(self.screen)

            subtitle = self.get_font(26).render(level["subtitle"], True, "gainsboro")
            subtitle_rect = subtitle.get_rect(midtop=(card_rect.centerx, card_rect.top + 130))
            self.screen.blit(subtitle, subtitle_rect)

            status = self.get_font(30).render(status_text, True, status_color)
            status_rect = status.get_rect(midbottom=(card_rect.centerx, card_rect.bottom - 20))
            self.screen.blit(status, status_rect)

        back_button.changeColor(mouse_pos)
        back_button.update(self.screen)

        self.screen.blit(title.title_text, title.title_text_rect)

        return buttons

    def draw_achievements(self, mouse_pos):
        self.screen.fill("black")

        title = MenuSetup(200, None, "Achievements", None, self.get_font(86), None, "white")

        gotta_start_somewhere_sprite = pygame.image.load("assets/achievements/gotta_start_somewhere.png", ).convert_alpha()
        gotta_start_somewhere_sprite = pygame.transform.scale(gotta_start_somewhere_sprite, (100, 100))

        rect_width = c.SCREEN_WIDTH // 9
        rect_height = c.SCREEN_HEIGHT // 6
        y_top = c.SCREEN_HEIGHT // 2.5
        y_bottom = c.SCREEN_HEIGHT // 1.5

        start_x = (c.SCREEN_WIDTH - (3 * rect_width + 2 * rect_width)) // 2

        for i in range(3):
            x = start_x + i * (rect_width * 2)
            pygame.draw.rect(self.screen, "lightblue1", (x, y_top, rect_width, rect_height), 0, border_radius=20)
        
        for i in range(3):
            x = start_x + i * (rect_width * 2)
            pygame.draw.rect(self.screen, "lightblue1", (x, y_bottom, rect_width, rect_height), 0, border_radius=20)
        
        BACK_BUTTON = Button(None, "<", (200, 200), self.get_font(200), "darkred", "red")
        
        buttons = [BACK_BUTTON]
        
        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        self.screen.blit(title.title_text, title.title_text_rect)

        self.screen.blit(gotta_start_somewhere_sprite, (start_x + 50, (y_top + y_bottom) / 2.5))
        
        achievement_desc = self.get_font(16).render("Gotta Start Somewhere", True, "white")
        achievement_desc_rect = achievement_desc.get_rect(center=(start_x + 100, (y_top + y_bottom) / 2.5 + 180))

        achievement_desc_completed = self.get_font(16).render("Not Completed", True, "red")
        achievement_desc_rect_completed = achievement_desc.get_rect(center=(start_x + 100, (y_top + y_bottom) / 2.5 + 200))

        self.screen.blit(achievement_desc, achievement_desc_rect)
        self.screen.blit(achievement_desc_completed, achievement_desc_rect_completed)

        return buttons

    def draw_settings(self, mouse_pos, settings_state, events):
        self.screen.fill("black")

        title = MenuSetup(200, None, "Settings", None, self.get_font(86), None, "white")

        pygame.draw.rect(self.screen, "white", (c.SCREEN_WIDTH // 8, 300, 300, 680), 0, border_radius=20)
        pygame.draw.rect(self.screen, "white", (c.SCREEN_WIDTH // 8 + 350, 300, 1080, 680), 0, border_radius=20)

        AUDIO_BUTTON = Button(None, "Audio", (c.SCREEN_WIDTH // 8 + 150, 450), self.get_font(48), "black", "#383838")
        self.screen.blit(title.title_text, title.title_text_rect)

        BACK_BUTTON = Button(None, "<", (200, 200), self.get_font(200), "darkred", "red")
        
        buttons = [BACK_BUTTON, AUDIO_BUTTON]
        
        if settings_state == "Audio":
            main_volume_title = self.get_font(48).render("Main Volume", True, "black")
            main_volume_title_rect = main_volume_title.get_rect(center=(c.SCREEN_WIDTH // 8 + 550, 330))

            if self.main_volume_slider is None:
                self.main_volume_slider = Slider(self.screen, c.SCREEN_WIDTH // 8 + 550, 420, 300, 20, min=0, max=100, step=1)

            main_volume_output = self.get_font(48).render(
                str(self.main_volume_slider.getValue()),
                True,
                "black"
            )
            main_volume_output_rect = main_volume_output.get_rect(
                center=(c.SCREEN_WIDTH // 8 + 1100, 430)
            )

            pygame_widgets.update(events)
            self.screen.blit(main_volume_output, main_volume_output_rect)
            self.screen.blit(main_volume_title, main_volume_title_rect)

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return buttons


    def draw_log_in(self, mouse_pos, username_input, password_input):
        self.screen.fill("black")

        pygame.draw.rect(
            self.screen, "#2e3f46",
            (c.SCREEN_WIDTH // 6, c.SCREEN_HEIGHT // 6, c.SCREEN_WIDTH // 1.5, c.SCREEN_HEIGHT // 1.5),
            border_radius=20
        )

        title = self.get_font(86).render("Antiparticle Annihilation", True, "white")
        title_rect = title.get_rect(center=(c.SCREEN_WIDTH // 2, 250))
        self.screen.blit(title, title_rect)

        username_input.draw(self.screen)
        password_input.draw(self.screen)

        login_button = Button(
            None, "Log In", (c.SCREEN_WIDTH // 2, 700),
            self.get_font(48), "white", "grey"
        )
        signup_button = Button(
            None, "Sign Up", (c.SCREEN_WIDTH // 2, 800),
            self.get_font(48), "white", "grey"
        )

        buttons = [login_button, signup_button]

        for b in buttons:
            b.changeColor(mouse_pos)
            b.update(self.screen)

        return buttons
    
    def draw_sign_up(self, mouse_pos, username_input, password_input):
        self.screen.fill("black")

        pygame.draw.rect(
            self.screen, "#2e3f46",
            (c.SCREEN_WIDTH // 6, c.SCREEN_HEIGHT // 6, c.SCREEN_WIDTH // 1.5, c.SCREEN_HEIGHT // 1.5),
            border_radius=20
        )

        title = self.get_font(86).render("Antiparticle Annihilation", True, "white")
        title_rect = title.get_rect(center=(c.SCREEN_WIDTH // 2, 250))
        self.screen.blit(title, title_rect)

        username_input.draw(self.screen)
        password_input.draw(self.screen)

        signup_button = Button(
            None, "Create Account", (c.SCREEN_WIDTH // 2, 700),
            self.get_font(48), "white", "grey"
        )
        back_button = Button(
            None, "Back to Login", (c.SCREEN_WIDTH // 2, 800),
            self.get_font(48), "white", "grey"
        )

        buttons = [signup_button, back_button]

        for b in buttons:
            b.changeColor(mouse_pos)
            b.update(self.screen)

        return buttons


