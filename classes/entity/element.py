import pygame
import math
from pygame.time import get_ticks
from data.element_data import ELEMENT_DATA

class Element(pygame.sprite.Sprite):
    def __init__(self, image, pos, name):
        super().__init__()

        self.name = name

        data = ELEMENT_DATA.get(name, {})

        self.is_damage = data.get("damage_element", False)
        self.is_healing = data.get("healing_element", False)
        self.is_energy = data.get("energy_element", False)

        self.energy_generation = data.get("energy_generation", 0)
        self.healing = data.get("healing", 0)

        self._last_action = 0  # shared timer for non-attack actions


        # Level / upgrade
        self.upgrade_level = 1
        # Use safe .get() lookups in case keys differ between data files
        self.upgrade_cost = ELEMENT_DATA.get(name, {}).get("upgrade_cost", 10)

        # range in pixels, cooldown in milliseconds, damage numeric
        self.range = ELEMENT_DATA.get(name, {}).get("range", 150)
        self.cooldown = ELEMENT_DATA.get(name, {}).get("cooldown", 1500)
        self.base_damage = ELEMENT_DATA.get(name, {}).get("damage", 1)
        self.damage = self.base_damage

        # sprite and rect
        self.image = image
        self.rect = self.image.get_rect(center=pos)

        # keep pos consistent with rect.center for distance checks

        self.max_health = data.get("hp", 100)
        self.health = self.max_health
        self.pos = tuple(self.rect.center)

        self.selected = False
        self.target = None

        # last shot timestamp (ms)
        self._last_shot = 0

        # range indicator surface (semi-transparent)
        self.range_image = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_image, (180, 180, 180, 100), (self.range, self.range), self.range)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

        # debug toggle
        self.debug = False

    def update(self, antiparticle_group, game):
        self.pos = self.rect.center
        self.range_rect.center = self.rect.center

        now = get_ticks()

        # ENERGY ELEMENT: generate energy passively
        if self.is_energy:
            if now - self._last_action >= self.cooldown:
                game.energy_amount += self.energy_generation
                self._last_action = now
            return  # energy towers do nothing else

        # HEALING ELEMENT: heal nearby elements
        if self.is_healing:
            if now - self._last_action >= self.cooldown:
                self.heal_nearby(game)
                self._last_action = now
            return

        # DAMAGE ELEMENT (default behavior)
        if self.is_damage:
            self.pick_target(antiparticle_group)
            if self.target:
                self.try_fire()


    def pick_target(self, antiparticle_group):
        closest = None
        closest_dist = float("inf")

        for ap in antiparticle_group:
            try:
                ap_x, ap_y = ap.rect.center
            except Exception:
                ap_x, ap_y = ap.pos[0], ap.pos[1]

            dx = ap_x - self.pos[0]
            dy = ap_y - self.pos[1]
            dist = math.hypot(dx, dy)

            if dist <= self.range and dist < closest_dist:
                closest = ap
                closest_dist = dist

        self.target = closest

        if self.debug and self.target:
            print(f"[DEBUG] {self.name} selected target at dist {closest_dist:.1f}")

    def try_fire(self):
        """Fire instantly at current target if cooldown has elapsed."""
        now = get_ticks()
        if now - self._last_shot < self.cooldown:
            return  # still cooling down

        # target might have died or been removed
        if not self.target or not getattr(self.target, "alive", lambda: True)():
            self.target = None
            return

        # Apply damage (instant hit)
        if hasattr(self.target, "take_damage"):
            self.target.take_damage(self.damage)
            if self.debug:
                print(f"[DEBUG] {self.name} hit {self.target} for {self.damage}")
        else:
            # fallback: try reducing a numeric health attribute
            if hasattr(self.target, "health"):
                self.target.health -= self.damage

        # record shot timestamp
        self._last_shot = now

    def upgrade(self):
        state = ELEMENT_DATA.get(self.name, {}).get("state", "Gas")

        if state == "Solid":
            self.upgrade_cost = math.floor(self.upgrade_cost * 1.35)
        elif state == "Liquid":
            self.upgrade_cost = math.floor(self.upgrade_cost * 1.275)
        else:
            self.upgrade_cost = math.floor(self.upgrade_cost * 1.2)
 
        self.range = math.floor(self.range * 1.0125)
        self.update_range()

        self.damage = math.floor(self.damage * 1.10)
        self.upgrade_level += 1
        

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_healthbar(surface)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

    def draw_healthbar(self, surface):
        bar_width = self.rect.width
        bar_height = 6
        x = self.rect.left
        y = self.rect.top - 10

        ratio = max(self.health / self.max_health, 0)

        # Background
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
        # Foreground
        pygame.draw.rect(surface, (50, 200, 50), (x, y, int(bar_width * ratio), bar_height))


    def update_range(self):
        self.range_image = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_image, (180, 180, 180, 100), (self.range, self.range), self.range)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

    def heal_nearby(self, game):
        for element in game.element_group:
            if element is self:
                continue

            dx = element.rect.centerx - self.rect.centerx
            dy = element.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            if dist <= self.range:
                if hasattr(element, "health") and hasattr(element, "max_health"):
                    element.health = min(
                        element.max_health,
                        element.health + self.healing
                    )

    def take_damage(self, amount):
        """Reduce element health and remove if dead."""
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        """Remove element and free occupied cell."""
        if hasattr(self, "cell") and self.cell in self.game_instance.occupied_cells:
            self.game_instance.occupied_cells.remove(self.cell)
        self.kill()
