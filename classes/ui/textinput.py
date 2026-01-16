import pygame

class TextInput:
    def __init__(self, x, y, w, h, font, placeholder="", password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color("grey60")
        self.color_active = pygame.Color("white")
        self.color = self.color_inactive
        self.text = ""
        self.font = font
        self.active = False
        self.password = password

        self.placeholder = placeholder
        self.placeholder_color = pygame.Color("grey30")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 18:  # max username/pass length
                    self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)

        if self.text == "":
            # Show placeholder when empty and NOT typing
            txt_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))
        else:
            # Normal typing
            display_text = "*" * len(self.text) if self.password else self.text
            txt_surface = self.font.render(display_text, True, pygame.Color("black"))
            screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

