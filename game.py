import asyncio
import classes.constants as c
import classes.managers.authentication_manager as auth
import classes.managers.database_manager as database_manager
import classes.managers.state_manager as state_manager
import classes.ui.text.text_utils as text
import pygame

from classes.entity.base import Base
from classes.entity.projectile import CombatProjectile
from classes.managers.asset_manager import Assets
from classes.managers.bonding_manager import BondingManager
from classes.managers.gameplay_manager import GameplayManager
from classes.ui.panels.question_panel import QuestionPanel
from classes.ui.panels.element_panel import ElementPanel
from classes.ui.game_error import GameError
from classes.ui.grid import Grid
from classes.ui.panels.compound_key_panel import CompoundKeyPanel
from classes.ui.panels.guide_panel import GuidePanel
from classes.ui.panels.hud_panel import HudPanel
from classes.ui.menus.menu import Menu
from classes.ui.menus.element_shop import ElementShop
from classes.ui.music import Music
from classes.ui.menus.pause_menu import PauseMenu
from classes.ui.tooltip import TooltipManager
from data.element_data import ELEMENT_DATA, SHOP_ELEMENT_ORDER
from data.map_data import MAP_DATA

pygame.init()
pygame.display.set_caption("Antiparticle Annihilation")

class MainLoop:
    def __init__(self):
        # Core
        self.screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.running = True
        self.clock = pygame.time.Clock()
        self.music = Music()

        # Grid & assets
        self.grid = Grid(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, cols=24, rows=14)
        self.assets = Assets(self.grid.cell_size)

        self.map = pygame.image.load("assets/map/grasslands.png").convert_alpha()
        self.map = pygame.transform.scale(self.map, (self.grid.grid_area_width, self.grid.grid_area_height + 25))

        database_manager.load_database(self)
        self.user_id = None
        self.current_username = ""
        self.element_shop_return_state = c.MAIN_MENU

        # State variables
        self.state = c.LOGIN
        self.settings_state = "Audio"
        self.paused = False
        self.selected_map = "tutorial"
        self.active_map_id = None
        self.research_amount = 0
        self.level_briefing_map_id = None
        self.unlocked_level_elements = []
        self.selected_level_elements = []
        self.level_briefing_enemy_scroll = 0
        self.level_briefing_loadout_scroll = 0
        self.question_session_total = 0
        self.question_session_index = 0
        self.question_return_state = c.GAMEPLAY
        self.achievement_notification_queue = []
        self.active_achievement_notification = None
        self.achievement_notification_started = 0
        self.achievement_notification_duration = 3600
        self.session_used_silicon = False
        self.session_used_glow_element = False

        # Map data
        self.first_lane_waypoints = []
        self.first_lane_cells = set()
        self.lane_waypoints = {}
        self.path_cells = set()

        # Error handling
        self.active_error = None
        self.error_start_time = None

        # Base entity
        self.base = None

        # selection variables
        self.selected_element = None
        self.selected_element_button = None
        self.selected_element_obj = None
        self.selected_element_obj_cost = None

        #  Sprite groups
        self.antiparticle_group = pygame.sprite.Group()
        self.element_group = pygame.sprite.Group()
        self.compounds = []
        self.projectiles = []
        self.pending_projectiles = []

        # Text line spacing
        self.LINE_HEIGHT = 25

        # Managers
        self.bonding_manager = BondingManager(self)
        self.gameplay = GameplayManager(self)
        self.load_map_configuration(self.selected_map, reset_runtime=False)

        # UI systems
        self.menu = Menu(self.screen, text.get_font, self.assets.icons["research"], self)
        self.element_shop = ElementShop(self, text.get_font, text.draw_wrapped_text)
        self.pause_menu = PauseMenu(self, text.get_font)
        self.question_panel = QuestionPanel(self, text.get_font, text.draw_wrapped_text)
        self.element_panel = ElementPanel(self, text.get_font, text.draw_centered_wrapped_text)
        self.hud_panel = HudPanel(self, text.get_font)
        self.guide_panel = GuidePanel(self, text.get_font, text.draw_wrapped_text)
        self.compound_key_panel = CompoundKeyPanel(self, text.get_font)
        self.tooltip_manager = TooltipManager(text.get_font)
        self.refresh_unlocked_level_elements()

    def apply_saved_audio_settings(self):
        if not self.user_id:
            return

        volume = database_manager.get_volume(self, self.user_id[0])
        self.music.update_volume(volume)
        self.menu.main_volume_slider.setValue(round(volume * 100))
        self.menu.main_volume_slider_value_saved = True

    def handle_events(self, events, mouse_pos, buttons):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel(mouse_pos, event.y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(mouse_pos, buttons)
            
            if event.type == pygame.KEYDOWN:
                self.handle_key_down(event)

            if self.state == c.LOGIN or self.state == c.SIGNUP:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    move_to_password = not self.menu.password_input.active
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        move_to_password = self.menu.password_input.active

                    self.menu.username_input.set_active(not move_to_password)
                    self.menu.password_input.set_active(move_to_password)
                    continue

                self.menu.username_input.handle_event(event)
                self.menu.password_input.handle_event(event)  

    def handle_mouse_wheel(self, mouse_pos, wheel_y):
        if self.state != c.LEVEL_BRIEFING:
            return

        hovered_panel = self.menu.get_level_briefing_scroll_panel(mouse_pos)
        if hovered_panel == "enemies":
            self.adjust_level_briefing_scroll("enemies", wheel_y)
        elif hovered_panel == "loadout":
            self.adjust_level_briefing_scroll("loadout", wheel_y)

    def handle_mouse_down(self, mouse_pos, buttons):
        if self.state == c.QUESTIONS:
            if self.question_panel.back_button and self.question_panel.back_button.checkForInput(mouse_pos):
                self.finish_question_session(cancelled=True)
                return

            if self.question_panel.next_button and self.question_panel.next_button.checkForInput(mouse_pos):
                if self.question_session_total > 0 and self.question_session_index >= self.question_session_total:
                    self.finish_question_session()
                else:
                    self.open_next_question()
                return

            if not self.question_panel.answered:
                for index, button in enumerate(self.question_panel.answer_buttons, start=1):
                    if button.checkForInput(mouse_pos):
                        self.question_panel.answer_current_question(index)
                        return

        if self.state == c.GAMEPLAY:
            if self.compound_key_panel.active:
                if self.compound_key_panel.close_button.checkForInput(mouse_pos):
                    self.compound_key_panel.close()
                    return

                # While the compound key is visible, block clicks from reaching gameplay UI.
                return

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

                        progress = {"tutorial": False}
                        if self.user_id:
                            progress = database_manager.get_user_level_progress(self, self.user_id[0])
                        tutorial_completed = progress.get("tutorial", False)
                        
                        if tutorial_completed:
                            self.state = c.LEVEL_SELECT
                            self.music.main_menu_music()
                        else:
                            self.state = c.MAIN_MENU
                            self.music.main_menu_music()

                        self.paused = False
                        return
                    if self.pause_menu.cancel_button.checkForInput(mouse_pos):
                        self.paused = False
                        return
                return

            for element_button in self.element_panel.element_buttons:
                if element_button.checkForInput(mouse_pos):
                    self.deselect_all_elements()
                    self.selected_element_button = element_button.element_key
                    self.selected_element = None
                    self.selected_element_obj = None
                    break

            for element in self.element_group:
                if element.rect.collidepoint(mouse_pos):
                    self.deselect_all_elements()
                    if element.compound:
                        element.compound.selected = True
                        self.selected_element_obj = element.compound
                    else:
                        element.selected = True
                        self.selected_element_obj = element

                    self.selected_element_button = None
                    self.selected_element = None

                    break

            if self.selected_element_obj is not None:
                if self.element_panel.upgrade_exit_button.checkForInput(mouse_pos):
                    self.deselect_all_elements()

                if self.element_panel.upgrade_button.checkForInput(mouse_pos):
                    upgrade_cost = self.selected_element_obj.upgrade_cost
                    if self.gameplay.energy_amount >= upgrade_cost:
                        self.selected_element_obj.upgrade()
                        if hasattr(self.selected_element_obj, "compound"):
                            self.bonding_manager.try_bond(self.selected_element_obj)
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

            if self.hud_panel.start_wave.checkForInput(mouse_pos) and not self.antiparticle_group and self.gameplay.current_wave == 0:
                self.gameplay.spawn_wave()

            if self.hud_panel.compound_key_button.checkForInput(mouse_pos):
                self.guide_panel.close_guide()
                self.compound_key_panel.open()

            if self.hud_panel.guide_button.checkForInput(mouse_pos):
                self.compound_key_panel.close()
                self.guide_panel.restart_guide()

            if self.hud_panel.speed_button.checkForInput(mouse_pos):
                self.gameplay.speed_mode = not self.gameplay.speed_mode

        for button in buttons: 
            if button.checkForInput(mouse_pos): state_manager.handle_button(self, button)

    def handle_key_down(self, event):
        if event.key == pygame.K_ESCAPE and self.state == c.GAMEPLAY and self.gameplay.pending_state is None:
            if self.guide_panel.active_guide_key is not None or self.compound_key_panel.active:
                self.guide_panel.close_guide()
                if self.compound_key_panel.active:
                    self.compound_key_panel.close()
                    return
            else:
                self.paused = not self.paused
        if event.key == pygame.K_ESCAPE and self.state == c.QUESTIONS:
            if not self.question_panel.require_session_completion:
                self.finish_question_session(cancelled=True)
        if event.key == pygame.K_RETURN:
            if self.state == c.LOGIN:
                auth.handle_login(self)
            elif self.state == c.SIGNUP:
                auth.handle_signup(self)

    async def run(self):
        try: 
            while self.running:
                dt = self.clock.tick(c.FPS) / 1000
                mouse_pos = pygame.mouse.get_pos()
                events = pygame.event.get()
                buttons = []

                if self.state != c.SETTINGS:
                    self.menu.hide_settings_widgets()
                if not self.paused:
                    self.pause_menu.hide_settings_widgets()

                # print("Menu music:", self.music.menu_music_channel.get_busy())
                # print("Question music:", self.music.question_music_channel.get_busy())
                # print("Game music:", self.music.gameplay_music_channel.get_busy())
                
                #region Handle menus rendering
                if self.state == c.MAIN_MENU:
                    buttons = self.menu.draw_main_menu(mouse_pos, self.current_username)
                elif self.state == c.DIFFICULTY_SELECT:
                    buttons = self.menu.draw_difficulty_select(mouse_pos)
                    # self.state = c.LEVEL_SELECT
                elif self.state == c.LEVEL_SELECT:
                    progress = {"tutorial": False}
                    if self.user_id:
                        progress = database_manager.get_user_level_progress(self, self.user_id[0])
                    buttons = self.menu.draw_level_select(mouse_pos, progress)
                elif self.state == c.LEVEL_BRIEFING:
                    briefing_map = MAP_DATA.get(self.level_briefing_map_id, MAP_DATA["tutorial"])
                    unlocked_lookup = {
                        element_name: True
                        for element_name in self.unlocked_level_elements
                    }
                    buttons = self.menu.draw_level_briefing(
                        mouse_pos,
                        briefing_map,
                        self.selected_level_elements,
                        unlocked_lookup,
                    )
                elif self.state == c.QUESTIONS:
                    buttons = self.question_panel.draw_question_boxes(mouse_pos)
                elif self.state == c.ELEMENT_SHOP:
                    buttons = self.element_shop.draw(mouse_pos, self.user_id, database_manager.get_user_research(self, self.user_id[0]))
                elif self.state == c.SETTINGS:
                    buttons = self.menu.draw_settings(mouse_pos, self.settings_state, events, self.music, self.user_id)
                elif self.state == c.ACHIEVEMENTS:
                    buttons = self.menu.draw_achievements(mouse_pos)
                elif self.state == c.LOGIN:
                    buttons = self.menu.draw_log_in(mouse_pos, self.menu.username_input, self.menu.password_input)
                elif self.state == c.SIGNUP:
                    buttons = self.menu.draw_sign_up(mouse_pos, self.menu.username_input, self.menu.password_input)
                #endregion

                self.handle_events(events, mouse_pos, buttons)
                    
                if self.state == c.GAMEPLAY:
                    self.ensure_map_loaded()
                    self.gameplay.update(dt, self.antiparticle_group, self.element_group, self.base)
                    self.render_gameplay(mouse_pos, events)

                if self.active_error is not None:
                    self.active_error.update(self.screen)

                    if pygame.time.get_ticks() - self.error_start_time > self.gameplay.game_over_delay:
                        self.active_error = None
                        self.error_start_time = None

                        if self.gameplay.pending_state == c.MAIN_MENU:
                            self.start_question_session(5, self.gameplay.pending_state, require_completion=True)

                self.draw_achievement_notification()
                            
                pygame.display.update()

                await asyncio.sleep(0)
        finally:
            # If game crashes, the database (if it has even loaded) will still save and close itself.
            if hasattr(self, "connection"):
                self.connection.commit()
                self.connection.close()

    def render_gameplay(self, mouse_pos, events):
        self.screen.fill("#252525")
        self.tooltip_manager.clear_targets()
        
        if self.active_map_id == "map1":
            self.screen.blit(self.map, self.grid.get_cell_top_left_corner(0,0))
            self.grid.draw(self.screen, self.grid, self.path_cells, self.assets, self.gameplay, False)
        else:
            self.grid.draw(self.screen, self.grid, self.path_cells, self.assets, self.gameplay, True)
        
        self.base.draw(self.screen)
        self.render_elements(mouse_pos)
        self.render_projectiles()
        self.render_antiparticles()
        self.hud_panel.draw(mouse_pos)
        self.element_panel.draw(mouse_pos)
        self.guide_panel.draw_feature_guide(mouse_pos)
        self.compound_key_panel.draw(mouse_pos)
        self.pause_menu.draw(mouse_pos, events)
        self.tooltip_manager.draw(self.screen, mouse_pos)

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

    def render_projectiles(self):
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def draw_achievement_notification(self):
        now = pygame.time.get_ticks()
        if self.active_achievement_notification is None and self.achievement_notification_queue:
            self.active_achievement_notification = self.achievement_notification_queue.pop(0)
            self.achievement_notification_started = now

        if self.active_achievement_notification is None:
            return

        if now - self.achievement_notification_started > self.achievement_notification_duration:
            self.active_achievement_notification = None
            return

        achievement = self.active_achievement_notification
        panel_rect = pygame.Rect(c.SCREEN_WIDTH - 470, 30, 420, 110)
        pygame.draw.rect(self.screen, "#17333d", panel_rect, border_radius=18)
        pygame.draw.rect(self.screen, "#78c8e3", panel_rect, 3, border_radius=18)

        icon = self.get_achievement_icon(achievement["name"])
        self.screen.blit(icon, (panel_rect.x + 16, panel_rect.y + 5))

        title = text.get_font(24).render("Achievement Unlocked", True, "white")
        reward = text.get_font(20).render(f"+{achievement['reward']} research", True, "#b8f7ba")
        name = text.get_font(20).render(achievement["name"], True, "#dff7ff")

        self.screen.blit(title, (panel_rect.x + 125, panel_rect.y + 14))
        self.screen.blit(name, (panel_rect.x + 125, panel_rect.y + 48))
        self.screen.blit(reward, (panel_rect.x + 125, panel_rect.y + 76))

    def deselect_all_elements(self):
        for element in self.element_group:
            element.selected = False
        for compound in self.compounds:
            compound.selected = False
        self.selected_element_obj = None

    def load_map_configuration(self, map_id, reset_runtime=True):
        map_data = MAP_DATA.get(map_id, MAP_DATA["tutorial"])
        self.selected_map = map_data["id"]
        self.active_map_id = map_data["id"]

        lane_cells = {}
        lane_paths = map_data.get("paths")

        if lane_paths is None:
            lane_paths = {"first": map_data["path_cells"]}

        self.lane_waypoints = {
            lane_name: [
                self.grid.get_cell_center(col, row)
                for col, row in path_cells
            ]
            for lane_name, path_cells in lane_paths.items()
        }

        lane_cells = {
            lane_name: self.grid.expand_path_cells(self.grid, waypoints)
            for lane_name, waypoints in self.lane_waypoints.items()
        }

        self.first_lane_waypoints = self.lane_waypoints.get("first", [])
        self.first_lane_cells = lane_cells.get("first", set())
        self.path_cells = set().union(*lane_cells.values()) if lane_cells else set()

        base_col, base_row = map_data.get("base_anchor_cell")
        base_pos = self.grid.get_cell_top_left_corner(base_col, base_row)
        self.base = Base(self, base_pos, self.assets.tiles["base"])

        self.gameplay.configure_for_map(map_data)

        if reset_runtime:
            self.gameplay.reset_level()
            self.paused = False

    def ensure_map_loaded(self):
        if self.active_map_id != self.selected_map:
            self.load_map_configuration(self.selected_map, reset_runtime=True)

    def start_question_session(self, total_questions, return_state, require_completion=False):
        self.question_session_total = max(0, total_questions)
        self.question_session_index = 0
        self.question_return_state = return_state
        self.question_panel.session_total = self.question_session_total
        self.question_panel.session_return_state = return_state
        self.question_panel.require_session_completion = require_completion
        self.question_panel.asked_question_ids = []
        self.state = c.QUESTIONS
        self.open_next_question()
        self.music.question_music()

    def open_next_question(self):
        if self.question_session_total > 0:
            self.question_session_index += 1
            self.question_panel.session_index = min(self.question_session_index, self.question_session_total)
        else:
            self.question_panel.session_index = 0
        self.question_panel.open_question()

    def finish_question_session(self, cancelled=False):
        return_state = self.question_return_state
        self.question_session_total = 0
        self.question_session_index = 0
        self.question_return_state = c.GAMEPLAY
        self.question_panel.session_total = 0
        self.question_panel.session_index = 0
        self.question_panel.session_return_state = c.GAMEPLAY
        self.question_panel.require_session_completion = False
        self.question_panel.asked_question_ids = []

        if return_state == c.MAIN_MENU and self.gameplay.pending_state == c.MAIN_MENU:
            self.gameplay.reset_level()
            self.paused = False
            self.state = c.MAIN_MENU
            self.gameplay.pending_state = None
            self.music.main_menu_music()
            return

        self.state = return_state if not cancelled else c.GAMEPLAY
        if self.state == c.GAMEPLAY:
            self.music.gameplay_music()

    def refresh_unlocked_level_elements(self):
        if self.user_id:
            unlocked_lookup = database_manager.get_user_unlocked_elements(self, self.user_id[0])
        else:
            unlocked_lookup = {
                element_name: data.get("default_unlocked", False)
                for element_name, data in ELEMENT_DATA.items()
            }

        self.unlocked_level_elements = [
            element_name
            for element_name in SHOP_ELEMENT_ORDER
            if unlocked_lookup.get(element_name) and element_name in self.assets.elements
        ]

        if not self.selected_level_elements:
            self.selected_level_elements = list(self.unlocked_level_elements[:3])

        self.selected_level_elements = [
            element_name
            for element_name in self.selected_level_elements
            if element_name in self.unlocked_level_elements
        ]

        if not self.selected_level_elements and self.unlocked_level_elements:
            self.selected_level_elements = [self.unlocked_level_elements[0]]

        self.element_panel.refresh_buttons()

    def open_level_briefing(self, map_id):
        self.level_briefing_map_id = map_id
        self.level_briefing_enemy_scroll = 0
        self.level_briefing_loadout_scroll = 0
        self.refresh_unlocked_level_elements()
        self.state = c.LEVEL_BRIEFING

    def toggle_level_element(self, element_name):
        if element_name not in self.unlocked_level_elements:
            return

        if element_name in self.selected_level_elements:
            if len(self.selected_level_elements) == 1:
                return
            self.selected_level_elements.remove(element_name)
        else:
            if len(self.selected_level_elements) >= 6:
                return
            self.selected_level_elements.append(element_name)

        self.element_panel.refresh_buttons()

    def adjust_level_briefing_scroll(self, panel_name, wheel_y):
        briefing_map = MAP_DATA.get(self.level_briefing_map_id, MAP_DATA["tutorial"])
        limits = self.menu.get_level_briefing_scroll_limits(
            briefing_map,
            self.unlocked_level_elements,
        )

        scroll_step = 84
        if panel_name == "enemies":
            max_scroll = limits.get("enemies", 0)
            self.level_briefing_enemy_scroll = min(
                max(self.level_briefing_enemy_scroll - (wheel_y * scroll_step), 0),
                max_scroll,
            )
        elif panel_name == "loadout":
            max_scroll = limits.get("loadout", 0)
            self.level_briefing_loadout_scroll = min(
                max(self.level_briefing_loadout_scroll - (wheel_y * scroll_step), 0),
                max_scroll,
            )

    def begin_selected_level(self):
        if not self.level_briefing_map_id:
            return

        self.selected_map = self.level_briefing_map_id
        self.session_used_silicon = False
        self.session_used_glow_element = False
        self.element_panel.refresh_buttons()
        self.state = c.GAMEPLAY
        self.music.gameplay_music()

    def spawn_projectile(self, origin, target, damage, source_name, knockback=0, **kwargs):
        self.projectiles.append(
            CombatProjectile(origin, target, damage, source_name, self, knockback=knockback, **kwargs)
        )

    def get_achievement_icon(self, achievement_name):
        key = self.assets._normalize_achievement_key(achievement_name)
        return self.assets.achievements.get(key, self.assets.achievements["placeholder"])

    def queue_achievement_notification(self, achievement):
        self.achievement_notification_queue.append(achievement)

    def unlock_achievement(self, achievement_name):
        if not self.user_id:
            return
        achievement = database_manager.unlock_user_achievement(self, self.user_id[0], achievement_name)
        if achievement is None:
            return

        self.research_amount = achievement["research_total"]
        if hasattr(self, "gameplay") and self.gameplay is not None:
            self.gameplay.research_amount = achievement["research_total"]
        self.queue_achievement_notification(achievement)

    def handle_element_placed(self, element_name):
        if element_name == "silicon":
            self.session_used_silicon = True
        if element_name in {"neon", "argon"}:
            self.session_used_glow_element = True

        if not self.user_id:
            return

        database_manager.increment_user_stat(self, self.user_id[0], "elements_placed")
        self.unlock_achievement("Gotta Start Somewhere")

    def handle_antiparticle_destroyed(self):
        if not self.user_id:
            return

        database_manager.increment_user_stat(self, self.user_id[0], "antiparticles_annihilated")
        stats = database_manager.get_user_statistics(self, self.user_id[0])
        self.unlock_achievement("Antiparticle Annihilation")
        if stats["antiparticles_annihilated"] >= 500:
            self.unlock_achievement("Antiparticle Antithesis")
        if stats["antiparticles_annihilated"] >= 10000:
            self.unlock_achievement("Baryon Asymmetry Solved")

    def handle_player_unit_destroyed(self):
        if not self.user_id:
            return

        database_manager.increment_user_stat(self, self.user_id[0], "particles_lost")
        self.unlock_achievement("...Particle Annihilation?")

    def handle_compound_created(self):
        if not self.user_id:
            return

        database_manager.increment_user_stat(self, self.user_id[0], "bonds_created")
        self.unlock_achievement("Syndistoicheiometry")

    def evaluate_level_completion_achievements(self):
        if not self.user_id:
            return

        if not self.session_used_silicon:
            self.unlock_achievement("Siligone")

        current_map = MAP_DATA.get(self.selected_map, {})
        if current_map.get("is_dark") and not self.session_used_glow_element:
            self.unlock_achievement("Lost in the Void")
