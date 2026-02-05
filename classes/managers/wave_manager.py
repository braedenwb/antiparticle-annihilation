import pygame
from entity.antiparticle import Antiparticle

class WaveManager:
    def __init__(self, assets):
        self.assets = assets
        self.spawn_queue = []
        self.current_wave = 0
        self.total_waves = 6
        self.sprite_map = assets.antiparticles

    def update(self, dt, antiparticle_group):
        current_time = pygame.time.get_ticks() / 1000
        for spawn in self.spawn_queue[:]:
            spawn_time, waypoints, type_name, sprite = spawn
            if current_time >= spawn_time:
                antiparticle_group.add(Antiparticle(waypoints, type_name, sprite))
                self.spawn_queue.remove(spawn)

    def spawn_wave(self, wave_number, waypoints):
        self.current_wave = wave_number
        wave_data = [("down_antiquark", waypoints, 25, 2.5)] * wave_number
        for i, (name, wps) in enumerate(wave_data):
            sprite = self.sprite_map[name]
            self.spawn_queue.append((pygame.time.get_ticks()/1000 + i*0.5, wps, name, sprite))
