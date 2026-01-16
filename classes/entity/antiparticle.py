import pygame
import classes.constants as c
from pygame.math import Vector2

from data.antiparticle_data import ANTIPARTICLE_DATA

class Antiparticle(pygame.sprite.Sprite):
    def __init__(self, waypoints, type_name, image):
        super().__init__()
        self.type_name = type_name
        data = ANTIPARTICLE_DATA[type_name]

        self.health = data["health"]
        self.max_health = self.health
        self.speed = data["speed"] * 50
        self.damage = data["damage"]
        self.attack_range = data["attack_range"]
        self.attack_cooldown = data["attack_cooldown"]
        self._last_attack = 0
        self.description = data["description"]
        self.hp_category = data["hp_category"]
        self.speed_category = data["speed_category"]

        self.image = image
        self.rect = self.image.get_rect(center=waypoints[0])
        self.pos = pygame.math.Vector2(self.rect.center)
        self.waypoints = waypoints
        self.target_waypoint = 1

    def update(self, dt, element_group):
        self.move(dt)
        self.try_attack(element_group)

    def try_attack(self, element_group):
        now = pygame.time.get_ticks()
        if now - self._last_attack < self.attack_cooldown:
            return

        closest = None
        closest_dist = float("inf")

        for element in element_group:
            dx = element.rect.centerx - self.rect.centerx
            dy = element.rect.centery - self.rect.centery
            dist = dx*dx + dy*dy

            if dist <= self.attack_range**2 and dist < closest_dist:
                closest = element
                closest_dist = dist
        
        if closest and hasattr(closest, "take_damage"):
            closest.take_damage(self.damage)
            self._last_attack = now

    def move(self, dt):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            movement = self.target - self.pos
        else:
            # Reached the end of the path. Base damage logic should begin here.
            self.kill()
            return

        distance = movement.length()
        move_amount = self.speed * dt

        if distance >= move_amount and distance != 0:
            self.pos += movement.normalize() * move_amount
        else:
            # Moves onto next waypoint.
            if distance != 0:
                self.pos += movement.normalize() * distance
            self.target_waypoint += 1

        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_healthbar(self, surface):
        bar_w = max(10, self.rect.width)
        bar_h = 4
        x = self.rect.left
        y = self.rect.top - 8
        pygame.draw.rect(surface, (100, 100, 100), (x, y, bar_w, bar_h))
        frac = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, (0, 200, 0), (x, y, int(bar_w * frac), bar_h))
