import asyncio
import classes.constants as c
import pygame # type: ignore
import os

from classes.antiparticle import Antiparticle
from classes.button import Button
from classes.element import Element
from classes.game_error import GameError
from classes.grid import Grid
from classes.menu import Menu
from classes.textinput import TextInput
from data.element_data import ELEMENT_DATA
from data.tutorial_steps import TUTORIAL_STEPS

pygame.init()

screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Antiparticle Annihilation")

tutorial_grid = Grid(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, cols=24, rows=14)

first_lane_waypoints = [
    tutorial_grid.get_cell_center(3,0), # Returns format (x, y)
    tutorial_grid.get_cell_center(3,8),
    tutorial_grid.get_cell_center(5,8),
    tutorial_grid.get_cell_center(5,2),
    tutorial_grid.get_cell_center(8,2),
    tutorial_grid.get_cell_center(8,8),
    tutorial_grid.get_cell_center(12,8),
    tutorial_grid.get_cell_center(12,3)
]

second_lane_waypoints = [
    tutorial_grid.get_cell_center(4,0),
    tutorial_grid.get_cell_center(4,3),
    tutorial_grid.get_cell_center(8,3),
    tutorial_grid.get_cell_center(8,6),
    tutorial_grid.get_cell_center(12,6),
    tutorial_grid.get_cell_center(12,3)
]

#region Sprite loading

antiparticle_group = pygame.sprite.Group()
element_group = pygame.sprite.Group()

# Icons
research_icon = pygame.image.load("assets/research.png").convert_alpha()
research_icon = pygame.transform.scale(research_icon, (100, 100))

energy_icon = pygame.image.load("assets/energy.png").convert_alpha()
energy_icon = pygame.transform.scale(energy_icon, (100, 100))

# Antiparticles
down_antiquark_sprite = pygame.image.load("assets/antiparticles/down_antiquark.png").convert_alpha()
down_antiquark_sprite = pygame.transform.scale(down_antiquark_sprite, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

up_antiquark_sprite = pygame.image.load("assets/antiparticles/up_antiquark.png").convert_alpha()
up_antiquark_sprite = pygame.transform.scale(up_antiquark_sprite, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

top_antiquark_sprite = pygame.image.load("assets/antiparticles/top_antiquark.png").convert_alpha()
top_antiquark_sprite = pygame.transform.scale(top_antiquark_sprite, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

SPRITE_MAP = {
    "down_antiquark": down_antiquark_sprite,
    "up_antiquark": up_antiquark_sprite,
    "top_antiquark": top_antiquark_sprite
}

# Elements
base_sprite = pygame.image.load("assets/base.png")
base_sprite = pygame.transform.scale(base_sprite, (1 * (tutorial_grid.cell_size), 1 * (tutorial_grid.cell_size)))

energy_tile_sprite = pygame.image.load("assets/energy_tile.png").convert_alpha()
energy_tile_sprite = pygame.transform.scale(energy_tile_sprite, (tutorial_grid.cell_size, tutorial_grid.cell_size))

hydrogen_sprite_large = pygame.image.load("assets/elements/hydrogen.png").convert_alpha()
hydrogen_sprite_button = pygame.transform.scale(hydrogen_sprite_large, (125, 125))
hydrogen_sprite = pygame.transform.scale(hydrogen_sprite_large, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

oxygen_sprite_large = pygame.image.load("assets/elements/oxygen.png").convert_alpha()
oxygen_sprite_button = pygame.transform.scale(oxygen_sprite_large, (125, 125))
oxygen_sprite = pygame.transform.scale(oxygen_sprite_large, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

silicon_sprite_large = pygame.image.load("assets/elements/silicon.png").convert_alpha()
silicon_sprite_button = pygame.transform.scale(silicon_sprite_large, (125, 125))
silicon_sprite = pygame.transform.scale(silicon_sprite_large, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

neodymium_sprite_large = pygame.image.load("assets/elements/neodymium.png").convert_alpha()
neodymium_sprite_button = pygame.transform.scale(neodymium_sprite_large, (150, 150))
neodymium_sprite = pygame.transform.scale(neodymium_sprite_large, (tutorial_grid.cell_size * 1.25, tutorial_grid.cell_size * 1.25))

#endregion

pygame.display.set_icon(base_sprite)

def get_font(size):
    return pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", size)

def draw_centered_wrapped_text(surface, text, font, color, rect, line_height):
        """
        Draws wrapped and horizontally centered text inside a rect,
        used for element descriptions / properties in the buy / upgrade menu.
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < rect.width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())

        y = rect.top
        for line in lines:
            rendered = font.render(line, True, color)
            text_rect = rendered.get_rect(centerx=rect.centerx, top=y)
            surface.blit(rendered, text_rect)
            y += line_height

class MainLoop:
    def __init__(self):
        self.running = True

        # Game state management variable
        # states: main_menu (default), difficulty_select, level_select, achievements & gameplay
        self.state = c.MAIN_MENU
        self.settings_state = "Audio" # state management variable for settings menu (Profiles, Audio, Clear All Data)
        self.active_error = None
        self.error_start_time = None

        self.occupied_cells = [
            (12,2), (13,2), # These coordinates
            (12,3), (13,3)  # are for the base
        ]
        self.energy_tiles = [
            (16,4),
            (1,11),
            (5,9),
            (2,8),
            (14,2),
            (13,10)
        ]

        self.selected_element = None
        self.selected_element_button = None
        self.spawn_queue = []

        self.energy_amount = 20 # starting amount is 20 for tutorial level

        self.clock = pygame.time.Clock()
        self.menu = Menu(
            screen,
            get_font,
            research_icon
        )

        self.grid = tutorial_grid

        self.username_input = TextInput(
            c.SCREEN_WIDTH // 2 - 150,
            c.SCREEN_HEIGHT // 2 - 50,
            300, 60,
            get_font(40),
            placeholder="Username"
        )

        self.password_input = TextInput(
            c.SCREEN_WIDTH // 2 - 150,
            c.SCREEN_HEIGHT // 2 + 50,
            300, 60,
            get_font(40),
            placeholder="Password",
            password=True
        )

        self.element_group = element_group

        self.paused = False
        self.pause_overlay = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.pause_overlay.set_alpha(180)
        self.pause_overlay.fill((0, 0, 0))

        self.current_wave = 0
        self.total_waves = 6
        self.tutorial_prompt = "Welcome! Buy a hydrogen (H) and place it near the red line and start a wave."
        self.prompt_start_time = 0

        self.PANEL_X = self.grid.side_margin // 3
        self.PANEL_Y = 25

        self.LINE_HEIGHT = 25

        # Left side buy menu element icons:
        self.hydrogen_select = Button(hydrogen_sprite_button, "", (self.grid.side_margin // 6, 75), get_font(32), "white", "grey")
        self.oxygen_select   = Button(oxygen_sprite_button, "", (self.grid.side_margin // 6, 200), get_font(32), "white", "grey")
        self.silicon_select  = Button(silicon_sprite_button, "", (self.grid.side_margin // 6, 350), get_font(32), "white", "grey")

        self.upgrade_exit_button = Button(None, "X", (self.PANEL_X + 275, self.PANEL_Y + 25), get_font(28), "red", "darkred")

    async def run(self):
        while self.running:
            dt = self.clock.tick(c.FPS) / 1000 # delta time
            mouse_pos = pygame.mouse.get_pos()
            buttons = []

            events = pygame.event.get()

            #region Handle menus rendering
            if self.state == c.MAIN_MENU:
                buttons = self.menu.draw_main_menu(mouse_pos, self.username_input.text)
            elif self.state == c.DIFFICULTY_SELECT:
                buttons = self.menu.draw_difficulty_select(mouse_pos)
            elif self.state == c.LEVEL_SELECT:
                buttons = self.menu.draw_level_select(mouse_pos)
            elif self.state == c.SETTINGS:
                buttons = self.menu.draw_settings(mouse_pos, self.settings_state, events)
            elif self.state == c.ACHIEVEMENTS:
                buttons = self.menu.draw_achievements(mouse_pos)
            elif self.state == c.LOGIN:
                buttons = self.menu.draw_log_in(mouse_pos, self.username_input, self.password_input)
            elif self.state == c.SIGNUP:
                buttons = self.menu.draw_sign_up(mouse_pos, self.username_input, self.password_input)
            #endregion

            if self.active_error is not None:
                self.active_error.update(screen)

                if pygame.time.get_ticks() - self.error_start_time > 3000:
                    self.active_error = None
                    self.error_start_time = None

            #region Gameplay
            if self.state == c.GAMEPLAY:

                ################################################################
                # Beginning of Rendering
                ################################################################
                
                screen.fill("#252525")

                pygame.draw.lines(screen, "red", False, first_lane_waypoints)

                self.grid.draw(screen)

                pygame.draw.rect(screen, "#445d68", (0, self.grid.grid_area_height, c.SCREEN_WIDTH, c.SCREEN_HEIGHT - self.grid.grid_area_height))
                pygame.draw.rect(screen, "#2e3f46", (0, self.grid.grid_area_height, c.SCREEN_WIDTH, c.SCREEN_HEIGHT - self.grid.grid_area_height), 4)
                pygame.draw.rect(screen, "#445d68", (0, 0, self.grid.side_margin, self.grid.grid_area_height))
                pygame.draw.rect(screen, "#2e3f46", (0, 0, self.grid.side_margin, self.grid.grid_area_height), 4)

                energy_text = get_font(54).render(str(self.energy_amount), True, "white")
                screen.blit(energy_text, (125, self.grid.grid_area_height + 25))
                screen.blit(energy_icon, (25, self.grid.grid_area_height + 20))

                research_text = get_font(54).render("0", True, "white")
                screen.blit(research_text, (125, self.grid.grid_area_height + 125))
                screen.blit(research_icon, (25, self.grid.grid_area_height + 120))

                selected_element_obj = None
                for element in element_group:
                    if getattr(element, "selected", False):
                        selected_element_obj = element
                        break

                if selected_element_obj:
                    text_rect = pygame.Rect(self.PANEL_X + 25, self.PANEL_Y + 160, 250, self.grid.grid_area_height - 180)

                    pygame.draw.rect(screen, "#405761", (self.PANEL_X, self.PANEL_Y, 300, self.grid.grid_area_height - 50), border_radius=15)
                    pygame.draw.rect(screen, "#2e3f46", (self.PANEL_X, self.PANEL_Y, 300, self.grid.grid_area_height - 50), 4, border_radius=15)

                    self.upgrade_exit_button.changeColor(mouse_pos)
                    self.upgrade_exit_button.update(screen)

                    title_text = get_font(28).render(f"{selected_element_obj.name.capitalize()}", True, "white")
                    title_text_rect = title_text.get_rect(center=(self.PANEL_X + 150, 45))
                    screen.blit(title_text, title_text_rect)

                    data = ELEMENT_DATA.get(selected_element_obj.name, {})

                    upgrade_button = Button(None, f"Upgrade for {selected_element_obj.upgrade_cost}", (self.PANEL_X + 150, self.PANEL_Y + 90), get_font(26), "white", "grey")
                    upgrade_button.changeColor(mouse_pos)
                    upgrade_button.update(screen)

                    if data['damage_element'] == True:
                        info_lines = [
                            f"Level: {selected_element_obj.upgrade_level}",
                            f"HP: {data['hp']}",
                            f"Damage: {selected_element_obj.damage}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]
                    elif data['healing_element'] == True:
                        info_lines = [
                            f"Level: {selected_element_obj.upgrade_level}",
                            f"HP: {data['hp']}",
                            f"Healing: {data['healing']}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]
                    elif data['energy_element'] == True:
                        info_lines = [
                            f"Level: {selected_element_obj.upgrade_level}",
                            f"HP: {data['hp']}",
                            f"Energy: {data['energy_generation']}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]

                    y_offset = text_rect.top
                    for line in info_lines:
                        draw_centered_wrapped_text(
                            screen,
                            line,
                            get_font(24),
                            "white",
                            pygame.Rect(text_rect.left, y_offset, text_rect.width, 60),
                            self.LINE_HEIGHT
                        )
                        y_offset += 40

                elif self.selected_element_button is not None:

                    pygame.draw.rect(screen, "#405761", (self.PANEL_X, self.PANEL_Y, 300, self.grid.grid_area_height - 50), border_radius=15)
                    pygame.draw.rect(screen, "#2e3f46", (self.PANEL_X, self.PANEL_Y, 300, self.grid.grid_area_height - 50), 4, border_radius=15)

                    title_text = get_font(28).render(f"{self.selected_element_button.capitalize()}", True, "white")
                    title_text_rect = title_text.get_rect(center=(self.PANEL_X + 150, 45))
                    screen.blit(title_text, title_text_rect)

                    data = ELEMENT_DATA.get(self.selected_element_button, {})

                    buy_exit_button = Button(None, "X", (self.PANEL_X + 275, self.PANEL_Y + 25), get_font(28), "red", "darkred")
                    buy_exit_button.changeColor(mouse_pos)
                    buy_exit_button.update(screen)

                    buy_cost = data.get("buy_cost", 0)
                    buy_button = Button(None, f"Buy for {buy_cost}", (self.PANEL_X + 150, self.PANEL_Y + 90), get_font(26), "white", "grey")
                    buy_button.changeColor(mouse_pos)
                    buy_button.update(screen)

                    text_rect = pygame.Rect(self.PANEL_X + 25, self.PANEL_Y + 160, 250, self.grid.grid_area_height - 200)

                    if data['damage_element'] == True:
                        info_lines = [
                            f"HP: {data['hp']}",
                            f"Damage: {data['damage']}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]
                    elif data['healing_element'] == True:
                        info_lines = [
                            f"HP: {data['hp']}",
                            f"Healing: {data['healing']}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]
                    elif data['energy_element'] == True:
                        info_lines = [
                            f"HP: {data['hp']}",
                            f"Energy: {data['energy_generation']}",
                            f"Cooldown: {data['cooldown'] / 1000:.1f}s",
                            f"State: {data['state']}",
                            data['desc']
                        ]

                    y_offset = text_rect.top
                    for line in info_lines:
                        draw_centered_wrapped_text(
                            screen,
                            line,
                            get_font(24),
                            "white",
                            pygame.Rect(text_rect.left, y_offset, text_rect.width, 60),
                            self.LINE_HEIGHT
                        )
                        y_offset += 40

                for energy_tile_coordinate in self.energy_tiles:
                    energy_tile_x, energy_tile_y = energy_tile_coordinate
                    screen.blit(energy_tile_sprite, (self.grid.get_cell_top_left_corner(energy_tile_x, energy_tile_y)))

                for button in [self.hydrogen_select, self.oxygen_select, self.silicon_select]:
                    button.update(screen)

                base_x, base_y = self.grid.get_cell_top_left_corner(12, 3)
                screen.blit(base_sprite, (base_x, base_y))

                run = Button(None, "Start Wave", (c.SCREEN_WIDTH // 1.2, 950), get_font(64), "white", "grey")
                run.changeColor(mouse_pos)
                run.update(screen)

                self.draw_tutorial_prompt()

                # Wave indicator
                wave_text = get_font(32).render(f"Wave {self.current_wave}/{self.total_waves}", True, "white")
                wave_rect = wave_text.get_rect(center=(c.SCREEN_WIDTH // 1.1, 1020))
                screen.blit(wave_text, wave_rect)

                # End of rendering

                if not self.paused:
                    if self.selected_element:
                        if self.selected_element == "hydrogen":
                            sprite = hydrogen_sprite
                        elif self.selected_element == "oxygen":
                            sprite = oxygen_sprite
                        elif self.selected_element == "silicon":
                            sprite = silicon_sprite
                        else:
                            sprite = hydrogen_sprite

                        rect = sprite.get_rect(center=mouse_pos)
                        sprite_copy = sprite.copy()
                        sprite_copy.set_alpha(150)
                        screen.blit(sprite_copy, rect)

                    for element in element_group:
                        element.draw(screen)
    
                    antiparticle_group.update(dt, element_group)
                    antiparticle_group.draw(screen)

                    for ap in antiparticle_group:
                        if hasattr(ap, "draw_healthbar"):
                            ap.draw_healthbar(screen)

                    element_group.update(antiparticle_group, self)

                    current_time = pygame.time.get_ticks() / 1000

                    for spawn in self.spawn_queue[:]:
                        spawn_time, waypoints, type_name, sprite = spawn
                        if current_time >= spawn_time:
                            ap = Antiparticle(waypoints, type_name, sprite)
                            antiparticle_group.add(ap)
                            self.spawn_queue.remove(spawn)

                if self.paused:
                    screen.blit(self.pause_overlay, (0, 0))

                    box_rect = pygame.Rect(
                        c.SCREEN_WIDTH // 2 - 300,
                        c.SCREEN_HEIGHT // 2 - 150,
                        600,
                        300
                    )

                    pygame.draw.rect(screen, "#2e3f46", box_rect, border_radius=15)
                    pygame.draw.rect(screen, "#445d68", box_rect, 4, border_radius=15)

                    title = get_font(36).render(
                        "Leave the game?",
                        True,
                        "white"
                    )
                    title_rect = title.get_rect(center=(box_rect.centerx, box_rect.top + 50))
                    screen.blit(title, title_rect)

                    text = get_font(24).render(
                        "All progress will be lost.",
                        True,
                        "white"
                    )
                    text_rect = text.get_rect(center=(box_rect.centerx, box_rect.centery - 10))
                    screen.blit(text, text_rect)

                    yes_button = Button(
                        None,
                        "Yes",
                        (box_rect.centerx - 100, box_rect.bottom - 60),
                        get_font(28),
                        "white",
                        "grey"
                    )

                    cancel_button = Button(
                        None,
                        "Cancel",
                        (box_rect.centerx + 100, box_rect.bottom - 60),
                        get_font(28),
                        "white",
                        "grey"
                    )

                    yes_button.changeColor(mouse_pos)
                    cancel_button.changeColor(mouse_pos)

                    yes_button.update(screen)
                    cancel_button.update(screen)


            #endregion

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == c.GAMEPLAY:
                        if self.hydrogen_select.checkForInput(mouse_pos):
                            self.deselect_all_elements()
                            self.selected_element_button = "hydrogen"
                            self.selected_element = None
                            continue

                        if self.oxygen_select.checkForInput(mouse_pos):
                            self.deselect_all_elements()
                            self.selected_element_button = "oxygen"
                            self.selected_element = None
                            continue

                        if self.silicon_select.checkForInput(mouse_pos):
                            self.deselect_all_elements()
                            self.selected_element_button = "silicon"
                            self.selected_element = None
                            continue

                        clicked_on_element = False
                        for element in element_group:
                            if element.rect.collidepoint(mouse_pos):
                                for e in element_group:
                                    e.selected = False
                                element.selected = True

                                self.selected_element_button = None
                                self.selected_element = None

                                clicked_on_element = True
                                break

                        if clicked_on_element:
                            continue

                        if selected_element_obj:
                            if self.upgrade_exit_button.checkForInput(mouse_pos):
                                self.deselect_all_elements()
                                continue

                            if upgrade_button.checkForInput(mouse_pos):
                                if self.energy_amount >= selected_element_obj.upgrade_cost:
                                    selected_element_obj.upgrade()
                                    self.energy_amount -= selected_element_obj.upgrade_cost
                                elif self.energy_amount < selected_element_obj.upgrade_cost:
                                    self.active_error = GameError("Not enough energy!")
                                    self.error_start_time = pygame.time.get_ticks()
                                continue

                        elif self.selected_element_button is not None:
                            if buy_exit_button.checkForInput(mouse_pos):
                                self.selected_element_button = None
                                continue

                            if buy_button.checkForInput(mouse_pos):
                                element_name = self.selected_element_button
                                cost = ELEMENT_DATA[element_name]["buy_cost"]

                                if self.energy_amount >= cost:
                                    self.energy_amount -= cost
                                    self.selected_element = element_name 
                                else:
                                    self.active_error = GameError("Not enough energy!")
                                    self.error_start_time = pygame.time.get_ticks()
                                continue

                        if self.selected_element:
                            cell = self.grid.get_cell_at_pos(mouse_pos)
                            if cell and cell not in self.occupied_cells:

                                col, row = cell
                                cx, cy = self.grid.get_cell_center(col, row)

                                sprite = {
                                    "hydrogen": hydrogen_sprite,
                                    "oxygen": oxygen_sprite,
                                    "silicon": silicon_sprite,
                                }.get(self.selected_element, hydrogen_sprite)

                                can_place = (
                                    (cell in self.energy_tiles and self.selected_element == "silicon") or
                                    (cell not in self.energy_tiles and self.selected_element != "silicon")
                                )

                                if can_place:
                                    new_element = Element(sprite, (cx, cy), self.selected_element)
                                    element_group.add(new_element)
                                    self.occupied_cells.append(cell)
                                    self.selected_element = None
                                else:
                                    self.active_error = GameError("Can't place here!")
                                    self.error_start_time = pygame.time.get_ticks()

                            continue

                        self.deselect_all_elements()

                        if run.checkForInput(mouse_pos):
                            self.spawn_wave()

                    if self.state == c.GAMEPLAY and self.paused:
                        if yes_button.checkForInput(mouse_pos):
                            self.paused = False
                            self.state = c.MAIN_MENU

                            antiparticle_group.empty()
                            element_group.empty()
                            self.spawn_queue.clear()

                            continue

                        if cancel_button.checkForInput(mouse_pos):
                            self.paused = False
                            continue

                        continue


                    for button in buttons: 
                        if button.checkForInput(mouse_pos): self.handle_button(button)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.state == c.GAMEPLAY:
                        self.paused = not self.paused


                if self.state == c.LOGIN or self.state == c.SIGNUP:
                    self.username_input.handle_event(event)
                    self.password_input.handle_event(event)  
            
            pygame.display.update()

            await asyncio.sleep(0)

    def draw_tutorial_prompt(self):
        if self.tutorial_prompt:
            font = get_font(28)
            text_surface = font.render(self.tutorial_prompt, True, "white")
            rect = text_surface.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT - 50))
            bg_rect = rect.inflate(20, 20)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, "white", bg_rect, 2)
            screen.blit(text_surface, rect)

    def spawn_wave(self):
        if self.current_wave < 6:
            self.current_wave += 1
            current_time = pygame.time.get_ticks() / 1000

            wave_data = []

            if self.current_wave == 1:
                wave_data = [("down_antiquark", first_lane_waypoints, 25, 2.5)] * 2
                self.energy_amount += 12
            elif self.current_wave == 2:
                wave_data = [("down_antiquark", first_lane_waypoints, 30, 2.5)] * 3
                self.energy_amount += 20
            elif self.current_wave == 3:
                wave_data = [("down_antiquark", first_lane_waypoints, 35, 3.0)] * 4
                self.energy_amount += 100
            elif self.current_wave == 4:
                wave_data = [("up_antiquark", first_lane_waypoints, 50, 2.0)] * 2
                self.energy_amount += 10
            elif self.current_wave == 5:
                wave_data = [("down_antiquark", first_lane_waypoints, 25, 3.0)] * 12
            elif self.current_wave == 6:
                wave_data = [("top_antiquark", first_lane_waypoints, 40, 2.5)]

            for i, (name, waypoints, health, speed) in enumerate(wave_data):
                sprite = SPRITE_MAP[name]
                self.spawn_queue.append((
                    current_time + i * 0.5, # 0.5 is time interval new enemies are spawned at
                    waypoints,
                    name,      
                    sprite
                ))

            self.tutorial_prompt = TUTORIAL_STEPS.get(self.current_wave, "")
            self.prompt_start_time = pygame.time.get_ticks()


    def deselect_all_elements(self):
        for element in element_group:
            element.selected = False


    def handle_button(self, button):
        """
            Handles all button logic
            according to what
            the game state is currently
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
                self.handle_login()
            elif button.text_input == "Sign Up":
                self.state = c.SIGNUP
        elif self.state == c.SIGNUP:
            if button.text_input == "Create Account":
                self.handle_signup()
            elif button.text_input == "Back to Login":
                self.state = c.LOGIN

    def handle_login(self):
        username = self.username_input.text
        password = self.password_input.text

        if username == "":
            self.active_error = GameError("Username cannot be empty")
            self.error_start_time = pygame.time.get_ticks()
            return
        
        if password == "":
            self.active_error = GameError("Password cannot be empty")
            self.error_start_time = pygame.time.get_ticks()
            return

        with open("accounts.txt", "r") as f:
            for line in f:
                stored_username, stored_password = line.strip().split(",")
                if username == stored_username:
                    if password == stored_password:
                        self.state = c.MAIN_MENU
                        return
                    else:
                        self.active_error = GameError("Incorrect password")
                        self.error_start_time = pygame.time.get_ticks()
                        return
        
        self.active_error = GameError("User not found")
        self.error_start_time = pygame.time.get_ticks()
                
    def handle_signup(self):
        username = self.username_input.text
        password = self.password_input.text

        if len(password) < 8:
            self.active_error = GameError("Password must be at least 8 characters")
            self.error_start_time = pygame.time.get_ticks()
            return

        with open("accounts.txt", "a") as f:
            f.write(f"{username},{password}\n")
        
        self.state = c.LOGIN