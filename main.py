"""
This file is for starting the game
and starting asyncio for web assembly. 
Prints out any errors to the console.
"""
import asyncio 
import pygame # type: ignore
from game import MainLoop 

async def main():
    loop = MainLoop() 
    try:
        await loop.run()
    except KeyboardInterrupt:   
        loop.running = False 
        print("Keyboard interrupt") 
    except pygame.error as err: 
        loop.running = False 
        print(f"Pygame error: {err}")   
        
asyncio.run(main())