"""
base.py

Defines the base at the end of the pre-defined path, acting as what you're protecting.

Author(s): Alan
Created: 2026-1-27
"""

import pygame

class Base(pygame.sprite.Sprite):
    """
    Set entity that stays at the end of the path. Preset health and will take damage
    upon the antiparticles entering or "colliding" into it.
    """
    def __init__(self, game, pos, image):
        super().__init__()
        self.game = game
        self.pos = pos
        self.max_health = 20
        self.health = 20
        self.base = "Base"
        
        self.image = image
        self.rect = self.image.get_rect(center=pos)
    
    def draw_healthbar(self, surface):
        bar_width = self.rect.width
        bar_height = 8
        x = self.pos[0]
        y = self.pos[1] * 0.95
        ratio = max(self.health / self.max_health, 0)

        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (50, 200, 50), (x, y, int(bar_width * ratio), bar_height))
    
    def draw(self, surface):
        surface.blit(self.image, self.pos)
        self.draw_healthbar(surface)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.game.lose_game()