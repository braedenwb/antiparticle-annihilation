"""
gameplay_manager.py

Manages game behaviour like the wave system,
win/lose conditions, and energy/research economy.

Author(s): Braeden
Created: 2026-02-17
"""

import classes.constants as c
import classes.managers.database_manager as database_manager
import pygame

from classes.entity.antiparticle import Antiparticle
from classes.entity.element import Element
from classes.ui.game_error import GameError
from data.element_data import ELEMENT_DATA

class GameplayManager:
    def __init__(self, main):
        self.main = main  # reference to MainLoop

        self.current_wave = 0
        self.total_waves = 6
        self.spawn_queue = []
        self.energy_amount = 20
        self.research_amount = 0

        self.win = False
        self.lose = False
        self.pending_state = None
        self.game_over_delay = 3000

        self.sprite_map = {
            name: self.main.assets.antiparticles[name]["grid"]
            for name in self.main.assets.antiparticles
        }

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

    def update(self, dt, antiparticle_group, element_group, base):
        if self.main.paused:
            return

        self.process_spawns()

        if (
            self.current_wave == self.total_waves
            and not self.spawn_queue
            and not self.main.antiparticle_group
        ):
            self.win_game()
        
        antiparticle_group.update(dt, element_group, base)
        element_group.update(self.main, antiparticle_group)

    def place_element(self, element_name, cell):
        if cell in self.occupied_cells:
            return False, "Cell occupied"

        cost = ELEMENT_DATA[element_name]["buy_cost"]

        if self.energy_amount < cost:
            return False, "Not enough energy"

        # placement rules
        if element_name == "silicon":
            if cell not in self.energy_tiles:
                return False, "Silicon must be on energy tile"
        else:
            if cell in self.energy_tiles:
                return False, "Only silicon allowed on energy tile"

        # Deduct energy
        self.energy_amount -= cost

        col, row = cell
        cx, cy = self.main.grid.get_cell_center(col, row)

        sprite = self.main.assets.elements[element_name]["grid"]

        new_element = Element(
            sprite,
            (cx, cy),
            element_name,
            self.main,
            cell
        )

        self.main.element_group.add(new_element)
        self.occupied_cells.append(cell)

        if hasattr(self.main, "bonding_manager") and self.main.bonding_manager is not None:
            self.main.bonding_manager.try_bond(new_element)

        return True, None

    def process_spawns(self):
        current_time = pygame.time.get_ticks() / 1000

        for spawn in self.spawn_queue[:]:
            spawn_time, waypoints, type_name, sprite = spawn
            if current_time >= spawn_time:
                ap = Antiparticle(waypoints, type_name, sprite)
                self.main.antiparticle_group.add(ap)
                self.spawn_queue.remove(spawn)

    def spawn_wave(self):
        if self.current_wave >= 6:
            return

        self.current_wave += 1
        current_time = pygame.time.get_ticks() / 1000

        wave_data = []

        if self.current_wave == 1:
            wave_data = [("down_antiquark", self.main.first_lane_waypoints, 25, 2.5)] * 2
            self.energy_amount += 12
        elif self.current_wave == 2:
            wave_data = [("down_antiquark", self.main.first_lane_waypoints, 30, 2.5)] * 3
            self.energy_amount += 30
        elif self.current_wave == 3:
            wave_data = [("down_antiquark", self.main.first_lane_waypoints, 35, 3.0)] * 4
            self.energy_amount += 100
        elif self.current_wave == 4:
            wave_data = [("up_antiquark", self.main.first_lane_waypoints, 50, 2.0)] * 2
            self.energy_amount += 10
        elif self.current_wave == 5:
            wave_data = [("down_antiquark", self.main.first_lane_waypoints, 25, 3.0)] * 12
        elif self.current_wave == 6:
            wave_data = [("top_antiquark", self.main.first_lane_waypoints, 40, 2.5)]

        for i, (name, waypoints, health, speed) in enumerate(wave_data):
            sprite = self.sprite_map[name]
            self.spawn_queue.append((
                current_time + i * 0.5,
                waypoints,
                name,
                sprite
            ))

    def win_game(self):
        if self.pending_state is not None:
            return

        if self.main.user_id and self.main.selected_map == "tutorial":
            database_manager.insert_user_level_progress(self.main, self.main.user_id[0])

        self.win = True
        self.lose = False
        self.main.paused = True

        self.main.active_error = GameError("")
        self.main.error_start_time = pygame.time.get_ticks()

        self.pending_state = c.MAIN_MENU

    def lose_game(self):
        if self.pending_state is not None:
            return

        self.lose = True
        self.win = False
        self.main.paused = True

        self.main.active_error = GameError("")
        self.main.error_start_time = pygame.time.get_ticks()

        self.pending_state = c.MAIN_MENU

    def award_research_for_correct_answer(self, amount=1):
        self.research_amount += amount

        if self.main.user_id:
            self.research_amount = database_manager.add_user_research(
                self.main,
                self.main.user_id[0],
                amount
            )

    def reset_level(self):
        self.main.antiparticle_group.empty()
        self.main.element_group.empty()
        self.spawn_queue.clear()

        self.main.base.health = self.main.base.max_health

        self.occupied_cells = [(12,2), (13,2), (12,3), (13,3)]
        self.main.selected_element = None
        self.main.selected_element_obj = None
        self.main.selected_element_button = None

        self.energy_amount = 20
        self.current_wave = 0
        self.win = False
        self.lose = False
        self.pending_state = None
