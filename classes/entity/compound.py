class Compound:
    def __init__(self, name, elements, stats, game):
        self.name = name
        self.elements = elements
        self.game = game

        self.max_health = stats["health"]
        self.health = self.max_health
        self.damage = stats.get("damage", 0)
        self.cooldown = stats.get("cooldown", 1000)

        self._last_action = 0

        for e in elements:
            e.compound = self
            e.health = self.health
            e.max_health = self.max_health

    def update(self, antiparticles):
        from pygame.time import get_ticks
        now = get_ticks()

        if now - self._last_action < self.cooldown:
            return

        for ap in antiparticles:
            for e in self.elements:
                dx = ap.rect.centerx - e.rect.centerx
                dy = ap.rect.centery - e.rect.centery
                if dx*dx + dy*dy < 150**2:
                    ap.take_damage(self.damage)
                    self._last_action = now
                    return


    def take_damage(self, amount):
        self.health -= amount

        for e in self.elements:
            e.health = self.health

        if self.health <= 0:
            self.destroy()

    def destroy(self):
        for e in self.elements:
            self.game.occupied_cells.remove(e.cell)
            e.kill()
        self.elements.clear()

