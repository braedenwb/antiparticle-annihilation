import classes.constants as c

class Draw_Menu:
    def __init__(self, title_y_pos, desc_y_pos, title_text, desc_text, title_font, desc_font, color):
        self.title_y_pos = title_y_pos
        self.color = color

        # Always required
        self.title_font = title_font
        self.title_text = self.title_font.render(title_text, True, self.color)
        self.title_text_rect = self.title_text.get_rect(center=(c.SCREEN_WIDTH // 2, self.title_y_pos))

        # Optional
        if desc_y_pos is not None and desc_text and desc_font:
            self.desc_y_pos = desc_y_pos
            self.desc_font = desc_font
            self.desc_text = desc_font.render(desc_text, True, self.color)
            self.desc_text_rect = self.desc_text.get_rect(center=(c.SCREEN_WIDTH // 2, self.desc_y_pos))
        else:
            self.desc_text = None
            self.desc_text_rect = None
