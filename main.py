"""
This file is the entrypoint for starting an instance
of the game and starting asyncio for web assembly. 
Prints out any errors to the console.
"""

import asyncio
import logging
import pygame

import classes.constants as c
from game import MainLoop

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def draw_loading_screen() -> None:
    pygame.init()
    pygame.display.set_caption("Antiparticle Annihilation")

    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    screen.fill("#0f171b")

    title_font = pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", 96)
    body_font = pygame.font.Font("assets/fonts/Orbitron-Medium.ttf", 36)

    title = title_font.render("Antiparticle Annihilation", True, "white")
    title_rect = title.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 - 80))
    screen.blit(title, title_rect)

    loading_text = body_font.render("Loading...", True, "#b8d0da")
    loading_rect = loading_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 30))
    screen.blit(loading_text, loading_rect)

    bar_rect = pygame.Rect(c.SCREEN_WIDTH // 2 - 220, c.SCREEN_HEIGHT // 2 + 90, 440, 18)
    fill_rect = pygame.Rect(bar_rect.left + 4, bar_rect.top + 4, bar_rect.width - 8, bar_rect.height - 8)
    pygame.draw.rect(screen, "#45606b", bar_rect, border_radius=10)
    pygame.draw.rect(screen, "#89b5c3", fill_rect, border_radius=8)

    pygame.display.update()
    pygame.event.pump()

async def main() -> None:
    draw_loading_screen()
    loop = MainLoop()
    try:
        await loop.run()
    except KeyboardInterrupt:
        loop.running = False
        print("Keyboard interrupt")
    except pygame.error as err:
        loop.running = False
        logger.critical("Pygame error: %s", err)
        print(f"Pygame error: {err}")
    except Exception as err:
        loop.running = False
        logger.critical("Unexpected error: %s", err, exc_info=True)
        print(f"Unexpected error: {err}")

asyncio.run(main())
