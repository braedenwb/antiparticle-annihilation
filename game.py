import asyncio
import classes.constants as c
import classes.managers.database_manager as database_manager
import classes.managers.state_manager as state_manager
import classes.ui.text.text_utils as text
import pygame

from classes.entity.base import Base
from classes.managers.asset_manager import Assets
from classes.managers.bonding_manager import BondingManager
from classes.managers.gameplay_manager import GameplayManager
from classes.ui.panels.question_panel import QuestionPanel
from classes.ui.panels.element_panel import ElementPanel
from classes.ui.game_error import GameError
from classes.ui.grid import Grid
from classes.ui.panels.guide_panel import GuidePanel
from classes.ui.panels.hud_panel import HudPanel
from classes.ui.menus.menu import Menu
from classes.ui.menus.pause_menu import PauseMenu
from data.element_data import ELEMENT_DATA

pygame.init()
pygame.display.set_caption("Antiparticle Annihilation")

class MainLoop:
    def __init__(self):
        # Core
        self.screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.running = True
        self.clock = pygame.time.Clock()

        # Grid & assets
        self.grid = Grid(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, cols=24, rows=14)
        self.assets = Assets(self.grid.cell_size)

        database_manager.load_database(self)
        self.user_id = None

        # pathing
        self.first_lane_waypoints = [
            self.grid.get_cell_center(3,0),
            self.grid.get_cell_center(3,8),
            self.grid.get_cell_center(5,8),
            self.grid.get_cell_center(5,2),
            self.grid.get_cell_center(8,2),
            self.grid.get_cell_center(8,8),
            self.grid.get_cell_center(12,8),
            self.grid.get_cell_center(12,3)
        ]
        self.first_lane_cells = self.grid.expand_path_cells(self.grid, self.first_lane_waypoints)

        # State variables
        self.state = c.LOGIN
        self.settings_state = "Audio"
        self.paused = False
        self.is_tutorial_complete = False
        self.selected_map = "tutorial"

        # Error handling
        self.active_error = None
        self.error_start_time = None

        # Base entity
        self.base_x, self.base_y = self.grid.get_cell_top_left_corner(12, 3)
        self.base = Base(self, (self.base_x, self.base_y), self.assets.tiles["base"])

        # selection variables
        self.selected_element = None
        self.selected_element_button = None
        self.selected_element_obj = None
        self.selected_element_obj_cost = None

        #  Sprite groups
        self.antiparticle_group = pygame.sprite.Group()
        self.element_group = pygame.sprite.Group()

        # Text line spacing
        self.LINE_HEIGHT = 25

        # Managers
        self.bonding_manager = BondingManager(self)
        self.gameplay = GameplayManager(self)

        # UI systems
        self.menu = Menu(self.screen, text.get_font, self.assets.icons["research"])
        self.pause_menu = PauseMenu(self, text.get_font)
        self.question_panel = QuestionPanel(self.screen)
        self.element_panel = ElementPanel(self, text.get_font, text.draw_centered_wrapped_text)
        self.hud_panel = HudPanel(self, text.get_font)
        self.guide_panel = GuidePanel(self, text.get_font, text.draw_wrapped_text)

    def handle_events(self, events, mouse_pos, buttons):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(mouse_pos, buttons)
            
            if event.type == pygame.KEYDOWN:
                self.handle_key_down(event)

            if self.state == c.LOGIN or self.state == c.SIGNUP:
                self.menu.username_input.handle_event(event)
                self.menu.password_input.handle_event(event)  

    def handle_mouse_down(self, mouse_pos, buttons):
        if self.state == c.GAMEPLAY:
            if self.guide_panel.active_guide_key is not None:
                if self.guide_panel.guide_close_button.checkForInput(mouse_pos):
                    self.guide_panel.close_guide()
                    return
                if self.guide_panel.guide_next_button.checkForInput(mouse_pos):
                    self.guide_panel.advance_guide()
                    return
                if self.guide_panel.guide_back_button.checkForInput(mouse_pos):
                    self.guide_panel.reverse_guide()
                    return

                # While guide is visible, block clicks from reaching gameplay UI.
                return

            if self.paused:
                if not self.gameplay.win and not self.gameplay.lose:
                    if self.pause_menu.yes_button.checkForInput(mouse_pos):
                        self.gameplay.reset_level()
                        self.state = c.MAIN_MENU
                        self.paused = False

                    if self.pause_menu.cancel_button.checkForInput(mouse_pos):
                        self.paused = False

            if self.element_panel.hydrogen_select.checkForInput(mouse_pos):
                self.deselect_all_elements()
                self.selected_element_button = "hydrogen"
                self.selected_element = None
                self.selected_element_obj = None

            if self.element_panel.oxygen_select.checkForInput(mouse_pos):
                self.deselect_all_elements()
                self.selected_element_button = "oxygen"
                self.selected_element = None
                self.selected_element_obj = None

            if self.element_panel.silicon_select.checkForInput(mouse_pos):
                self.deselect_all_elements()
                self.selected_element_button = "silicon"
                self.selected_element = None
                self.selected_element_obj = None

            for element in self.element_group:
                if element.rect.collidepoint(mouse_pos):
                    for e in self.element_group:
                        e.selected = False
                    element.selected = True
                    self.selected_element_obj = element

                    self.selected_element_button = None
                    self.selected_element = None

                    break

            if self.selected_element_obj is not None:
                if self.element_panel.upgrade_exit_button.checkForInput(mouse_pos):
                    self.deselect_all_elements()
                    self.selected_element_obj = None

                if self.element_panel.upgrade_button.checkForInput(mouse_pos):
                    upgrade_cost = self.selected_element_obj.upgrade_cost
                    if self.gameplay.energy_amount >= upgrade_cost:
                        self.selected_element_obj.upgrade()
                        self.gameplay.energy_amount -= upgrade_cost
                    elif self.gameplay.energy_amount < upgrade_cost:
                        self.active_error = GameError("Not enough energy!")
                        self.error_start_time = pygame.time.get_ticks()

            elif self.selected_element_button is not None:
                if self.element_panel.buy_exit_button.checkForInput(mouse_pos):
                    self.selected_element_button = None

                if self.element_panel.buy_button.checkForInput(mouse_pos):
                    element_name = self.selected_element_button
                    cost = ELEMENT_DATA[element_name]["buy_cost"]

                    if self.gameplay.energy_amount >= cost:
                        self.selected_element = element_name 
                    else:
                        self.active_error = GameError("Not enough energy!")
                        self.error_start_time = pygame.time.get_ticks()

            if self.selected_element:
                cell = self.grid.get_cell_at_pos(mouse_pos)
                if cell:
                    success, error = self.gameplay.place_element(self.selected_element, cell)

                    if not success:
                        self.active_error = GameError(error)
                        self.error_start_time = pygame.time.get_ticks()
                    else:
                        self.selected_element = None

            if self.hud_panel.start_wave.checkForInput(mouse_pos) and not self.antiparticle_group:
                self.gameplay.spawn_wave()

            if self.hud_panel.answer_questions.checkForInput(mouse_pos):
                self.state = c.QUESTIONS

            if self.hud_panel.guide_button.checkForInput(mouse_pos):
                self.guide_panel.restart_guide()

        for button in buttons: 
            if button.checkForInput(mouse_pos): state_manager.handle_button(self, button)

    def handle_key_down(self, event):
        if event.key == pygame.K_ESCAPE and self.state == c.GAMEPLAY and self.gameplay.pending_state is None:
            self.paused = not self.paused
        if event.key == pygame.K_ESCAPE and self.state == c.QUESTIONS:
            self.state = c.GAMEPLAY

    async def run(self):
        try: 
            while self.running:
                dt = self.clock.tick(c.FPS) / 1000
                mouse_pos = pygame.mouse.get_pos()
                events = pygame.event.get()
                buttons = []
                
                #region Handle menus rendering
                if self.state == c.MAIN_MENU:
                    buttons = self.menu.draw_main_menu(mouse_pos, self.menu.username_input.text)
                elif self.state == c.DIFFICULTY_SELECT:
                    buttons = self.menu.draw_difficulty_select(mouse_pos)
                elif self.state == c.LEVEL_SELECT:
                    progress = {"tutorial": False}
                    if self.user_id:
                        progress = database_manager.get_user_level_progress(self, self.user_id[0])
                    buttons = self.menu.draw_level_select(mouse_pos, progress)
                elif self.state == c.QUESTIONS:
                    buttons = self.question_panel.draw_question_boxes(mouse_pos)
                elif self.state == c.SETTINGS:
                    buttons = self.menu.draw_settings(mouse_pos, self.settings_state, events)
                elif self.state == c.ACHIEVEMENTS:
                    buttons = self.menu.draw_achievements(mouse_pos)
                elif self.state == c.LOGIN:
                    buttons = self.menu.draw_log_in(mouse_pos, self.menu.username_input, self.menu.password_input)
                elif self.state == c.SIGNUP:
                    buttons = self.menu.draw_sign_up(mouse_pos, self.menu.username_input, self.menu.password_input)
                #endregion

                self.handle_events(events, mouse_pos, buttons)

                if self.active_error is not None:
                    self.active_error.update(self.screen)

                    if pygame.time.get_ticks() - self.error_start_time > self.gameplay.game_over_delay:
                        self.active_error = None
                        self.error_start_time = None

                        if self.gameplay.pending_state == c.MAIN_MENU:
                            self.gameplay.reset_level()
                            self.paused = False
                            self.state = c.MAIN_MENU
                            self.gameplay.pending_state = None
                    
                if self.state == c.GAMEPLAY:
                    self.gameplay.update(dt, self.antiparticle_group, self.element_group, self.base)
                    self.render_gameplay(mouse_pos)
                pygame.display.update()

                await asyncio.sleep(0)
        finally:
            # If game crashes, the database (if it has even loaded) will still save and close itself.
            if hasattr(self, "connection"):
                self.connection.commit()
                self.connection.close()

    def render_gameplay(self, mouse_pos):
        self.screen.fill("#252525")
        
        self.grid.draw(self.screen, self.grid, self.first_lane_cells, self.assets, self.gameplay)
        self.base.draw(self.screen)
        self.render_elements(mouse_pos)
        self.render_antiparticles()
        self.hud_panel.draw(mouse_pos)
        self.element_panel.draw(mouse_pos)
        self.guide_panel.draw_feature_guide(mouse_pos)
        self.pause_menu.draw(mouse_pos)

    def render_elements(self, mouse_pos):
        if not self.paused and self.selected_element:
            sprite = self.assets.elements[self.selected_element]["grid"]
            rect = sprite.get_rect(center=mouse_pos)
            sprite_copy = sprite.copy()
            sprite_copy.set_alpha(150)

            range = ELEMENT_DATA.get(self.selected_element, {}).get("range", 150)
            range_image = pygame.Surface((range * 2, range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_image, (180, 180, 180, 100), (range, range), range)
            range_rect = range_image.get_rect(center=rect.center)
            self.screen.blit(range_image, range_rect)
            self.screen.blit(sprite_copy, rect)

        for element in self.element_group:
            element.draw(self.screen)

    def render_antiparticles(self):
        for ap in self.antiparticle_group:
            ap.draw(self.screen)

    def deselect_all_elements(self):
        for element in self.element_group:
            element.selected = False
        self.selected_element_obj = None
