from classes.antiparticle import Antiparticle
import asyncio
from classes.element import Element
import json
import pygame
import classes.constants as c
from classes.button import Button

pygame.init()

clock = pygame.time.Clock() 

screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pygame.display.set_caption("Antiparticle Annihilation")

font = pygame.font.SysFont("Consolas", 64)

# load sprites
hydrogen = pygame.image.load("assets/hydrogen.png").convert_alpha()
hydrogen = pygame.transform.scale(hydrogen, (100, 100))

down_antiquark_image = pygame.image.load("assets/down_antiquark.png").convert_alpha()
down_antiquark_image = pygame.transform.scale(down_antiquark_image, (100, 100))

down_antiquark = Antiparticle((200, 300), down_antiquark_image)

# Game loop
on_main_menu = True
run = True

def get_font(size):
    return pygame.font.SysFont("Consolas", size)

def play():
    screen.fill("black")
    screen.blit(hydrogen, (200, 200))
    screen.blit(down_antiquark_image, (300, 200))

def main_menu(mouse_pos):
    screen.fill("black")

    MENU_TITLE = font.render("Antiparticle Annihilation", True, (255, 255, 255))
    MENU_TITLE_RECT = MENU_TITLE.get_rect(center=(c.SCREEN_WIDTH // 2, 200))

    PLAY_BUTTON = Button("PLAY", (c.SCREEN_WIDTH // 2, 300), get_font(64), "white", "grey")
    LOAD_DATA_BUTTON = Button("LOAD DATA", (c.SCREEN_WIDTH // 2, 400), get_font(64), "white", "grey")
    SETTINGS_BUTTON = Button("SETTINGS", (c.SCREEN_WIDTH // 2, 500), get_font(64), "white", "grey")
    ACHIEVEMENTS_BUTTON = Button("ACHIEVEMENTS", (c.SCREEN_WIDTH // 2, 600), get_font(64), "white", "grey")
    QUIT_BUTTON = Button("QUIT", (c.SCREEN_WIDTH // 2, 700), get_font(64), "white", "grey")

    buttons = [PLAY_BUTTON, LOAD_DATA_BUTTON, SETTINGS_BUTTON, ACHIEVEMENTS_BUTTON, QUIT_BUTTON]

    for button in buttons:
        button.changeColor(mouse_pos)
        button.update(screen)

    screen.blit(MENU_TITLE, MENU_TITLE_RECT)

    return buttons

async def main():
    global run, on_main_menu
    buttons = []

    while run:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.checkForInput(mouse_pos):
                        if button.text_input == "PLAY":
                            on_main_menu = False
                        elif button.text_input == "LOAD DATA":
                            pass
                        elif button.text_input == "SETTINGS":
                            pass
                        elif button.text_input == "ACHIEVEMENTS":
                            pass
                        elif button.text_input == "QUIT":
                            run = False

        if on_main_menu:
            buttons = main_menu(mouse_pos)
        else:
            play()

        pygame.display.flip()
        clock.tick(c.FPS)
        await asyncio.sleep(0)

asyncio.run(main())
pygame.quit()
