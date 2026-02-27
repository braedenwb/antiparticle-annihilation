from classes.entity.compound import Compound

class BondingManager:
    def __init__(self, game):
        self.game = game

    def get_neighbors(self, element):
        x, y = element.cell
        neighbors = []

        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            cell = (x + dx, y + dy)
            for neighbor in self.game.element_group:
                if getattr(neighbor, "cell", None) == cell:
                    neighbors.append(neighbor)
                    break

        return neighbors
    
    def try_bond(self, element):
        if element.compound:
            return

        for neighbor in self.get_neighbors(element):
            if neighbor.compound:
                continue

            self.check_pair(element, neighbor)

    def check_pair(self, a, b):
        names = {a.name, b.name}

        if names == {"hydrogen", "oxygen"}:
            if a.upgrade_level >= 2 or b.upgrade_level >= 2:
                self.create_water(a, b)

    def create_water(self, a, b):
        stats = {
            "health": 120,
            "damage": 6,
            "cooldown": 1200
        }

        compound = Compound(
            name="water",
            elements=[a, b],
            stats=stats,
            game=self.game
        )

        if not hasattr(self.game, "compounds"):
            self.game.compounds = []
        self.game.compounds.append(compound)



