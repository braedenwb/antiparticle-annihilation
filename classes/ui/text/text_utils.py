import pygame

def get_font(size):
    return pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", size)

def draw_centered_wrapped_text(surface, text, font, color, rect, line_height):
        """
        Draws wrapped and horizontally centered text inside a rect,
        used for element descriptions / properties in the buy / upgrade menu.
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < rect.width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())

        y = rect.top
        for line in lines:
            rendered = font.render(line, True, color)
            text_rect = rendered.get_rect(centerx=rect.centerx, top=y)
            surface.blit(rendered, text_rect)
            y += line_height

def draw_wrapped_text(surface, text, font, color, rect, line_height):
        words = text.split(" ")
        line = ""
        y = rect.top

        for word in words:
            test_line = f"{line}{word} "
            if font.size(test_line)[0] <= rect.width:
                line = test_line
            else:
                rendered = font.render(line.strip(), True, color)
                surface.blit(rendered, (rect.left, y))
                y += line_height
                line = f"{word} "

        if line:
            rendered = font.render(line.strip(), True, color)
            surface.blit(rendered, (rect.left, y))