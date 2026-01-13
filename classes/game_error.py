import classes.constants as c
import pygame

class GameError():
    def __init__(self, error_text):
        self.error_text = error_text
        self.font = pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", 64)
        
        self.x_pos = c.SCREEN_WIDTH // 2
        self.y_pos = c.SCREEN_HEIGHT // 3

        self.text = self.font.render(self.error_text, True, "#C56D6D")
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, surface):
        surface.blit(self.text, self.text_rect)

