import pygame

class Grid:
    def __init__(self, screen_width, screen_height, cols, rows, bottom_margin=250):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cols = cols
        self.rows = rows
        self.bottom_margin = bottom_margin

        # grid height (stops above bottom margin)
        self.grid_area_height = self.screen_height - self.bottom_margin

        # pick cell size based on available height
        self.cell_height = self.grid_area_height // self.rows
        self.cell_width = self.cell_height  # keep square cells
        self.cell_size = self.cell_height

        # compute grid width and dynamic side margin
        self.grid_area_width = self.cell_size * self.cols
        self.side_margin = self.screen_width - self.grid_area_width  # leftover space

        # place grid so it touches the right edge
        self.x = self.side_margin
        self.y = 0

        # build cells
        self.cells = [
            pygame.Rect(self.x + c * self.cell_size,
                        self.y + r * self.cell_size,
                        self.cell_size, self.cell_size)
            for r in range(self.rows)
            for c in range(self.cols)
        ]

    def draw(self, surface, grid, cells, assets, gameplay, grid_color=(180, 180, 180)):
        self.draw_path(surface, grid, cells)

        for row in range(self.rows + 1):
            y = self.y + row * self.cell_size
            pygame.draw.line(surface, grid_color,
                             (self.x, y),
                             (self.x + self.cols * self.cell_size, y), 1)

        for col in range(self.cols + 1):
            x = self.x + col * self.cell_size
            pygame.draw.line(surface, grid_color,
                             (x, self.y),
                             (x, self.y + self.rows * self.cell_size), 1)
        
        self.draw_energy_tiles(assets, gameplay, surface)

    def draw_path(self, surface, grid, cells):
        for col, row in cells:
            rect = pygame.Rect(
                grid.get_cell_top_left_corner(col, row),
                (grid.cell_size, grid.cell_size)
            )
            pygame.draw.rect(surface, (255, 255, 255), rect)

    def draw_energy_tiles(self, assets, gameplay, surface):
        energy_tile = assets.tiles.get("energy_tile")
        if energy_tile:
            for col, row in gameplay.energy_tiles:
                pos = self.get_cell_top_left_corner(col, row)
                surface.blit(energy_tile, pos)

    def expand_path_cells(self, grid, waypoints):
        cells = set()

        waypoint_cells = [
            grid.get_cell_from_center(p)
            for p in waypoints
        ]

        for (c1, r1), (c2, r2) in zip(waypoint_cells, waypoint_cells[1:]):
            if c1 == c2:
                step = 1 if r2 > r1 else -1
                for r in range(r1, r2 + step, step):
                    cells.add((c1, r))

            elif r1 == r2:
                step = 1 if c2 > c1 else -1
                for c in range(c1, c2 + step, step):
                    cells.add((c, r1))

        return cells

    def get_cell_at_pos(self, pos):
        mx, my = pos
        if not (self.x <= mx < self.x + self.cols * self.cell_size and
                self.y <= my < self.y + self.rows * self.cell_size):
            return None
        col = (mx - self.x) // self.cell_size
        row = (my - self.y) // self.cell_size
        return (col, row)
    
    def get_cell_center(self, col, row):
        x = self.x + col * self.cell_size + self.cell_size // 2
        y = self.y + row * self.cell_size + self.cell_size // 2
        return (x, y)
    
    def get_cell_at_center(self, pos):
        x, y = pos
        col = (x - self.side_margin) // self.cell_size
        row = y // self.cell_size
        return int(col), int(row)

    def get_cell_from_center(self, pos):
        x, y = pos
        col = (x - self.x) // self.cell_size
        row = (y - self.y) // self.cell_size
        return int(col), int(row)

    def get_cell_top_left_corner(self, col, row):
        x = self.x + col * self.cell_size
        y = self.y + row * self.cell_size
        return (x, y)

