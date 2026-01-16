class Button:
    def __init__(self, image, text_input, pos, font, base_color, hover_color):
        self.image = image
        self.text_input = text_input
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color

        self.text = self.font.render(self.text_input, True, self.base_color)

        if self.image:
            self.rect = self.image.get_rect(center=pos)
        else:
            self.rect = self.text.get_rect(center=pos)

        self.text_rect = self.text.get_rect(center=self.rect.center)

    def update(self, screen):
        self.text_rect = self.text.get_rect(center=self.rect.center)

        if self.image:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hover_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

    def set_text(self, new_text):
        self.text_input = new_text
        self.text = self.font.render(self.text_input, True, self.base_color)

        if not self.image:
            self.rect = self.text.get_rect(center=self.rect.center)

        self.text_rect = self.text.get_rect(center=self.rect.center)
