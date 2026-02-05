"""
asset_manager.py

Loads all game assets and adds them to 
dictionarys by their category

Author(s): Alan
Created: 2026-01-22
"""

import pygame

class Assets:
    def __init__(self, cell_size):
        self.cell_size = cell_size

        self.icons = {}
        self.antiparticles = {}
        self.elements = {}
        self.tiles = {}

        self._load_icons()
        self._load_antiparticles()
        self._load_elements()
        self._load_tiles()

    def _load_image(self, path):
        return pygame.image.load(path).convert_alpha()

    def _scale(self, image, size):
        return pygame.transform.smoothscale(image, size)

    def _load_icons(self):
        research = self._load_image("assets/icons/research.png")
        energy = self._load_image("assets/icons/energy.png")

        self.icons["research"] = self._scale(research, (100, 100))
        self.icons["energy"] = self._scale(energy, (100, 100))

    def _load_antiparticles(self):
        base = {
            "down_antiquark": "assets/antiparticles/down_antiquark.png",
            "up_antiquark": "assets/antiparticles/up_antiquark.png",
            "top_antiquark": "assets/antiparticles/top_antiquark.png",
        }

        for name, path in base.items():
            raw = self._load_image(path)

            self.antiparticles[name] = {
                "grid": self._scale(raw, (int(self.cell_size * 1.25), int(self.cell_size * 1.25))),
                "button": self._scale(raw, (100, 100)),
                "large": raw
            }

    def _load_elements(self):
        base = {
            "hydrogen": "assets/elements/hydrogen.png",
            "oxygen": "assets/elements/oxygen.png",
            "silicon": "assets/elements/silicon.png",
            "neodymium": "assets/elements/neodymium.png",
        }

        for name, path in base.items():
            raw = self._load_image(path)

            self.elements[name] = {
                "grid": self._scale(raw, (int(self.cell_size * 1.25), int(self.cell_size * 1.25))),
                "button": self._scale(raw, (125, 125)),
                "large": raw
            }

    def _load_tiles(self):
        base = self._load_image("assets/map/base.png")
        energy_tile = self._load_image("assets/map/energy_tile.png")

        size = (self.cell_size, self.cell_size)

        self.tiles["base"] = self._scale(base, size)
        self.tiles["energy_tile"] = self._scale(energy_tile, size)
