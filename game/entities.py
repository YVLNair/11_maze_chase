import pygame
from game.maze import CELL

class Player:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.speed = 6

        cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
        self.rect = pygame.Rect(cx - 10, cy - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed

        if dx == 0 and dy == 0:
            return

        # Try horizontal movement
        new_rect = self.rect.move(dx, 0)

        if self._valid(new_rect, walls, rows, cols):
            self.rect = new_rect

        # Try vertical movement
        new_rect = self.rect.move(0, dy)

        if self._valid(new_rect, walls, rows, cols):
            self.rect = new_rect

        # Update cell coordinates from pixel position
        self.c = self.rect.centerx // CELL
        self.r = self.rect.centery // CELL

    def _valid(self, rect, walls, rows, cols):
        # Keep player inside the maze
        if rect.left < 0 or rect.right > cols * CELL:
            return False

        if rect.top < 0 or rect.bottom > rows * CELL:
            return False

        # Determine cells occupied by the player's rectangle
        left = rect.left // CELL
        right = (rect.right - 1) // CELL
        top = rect.top // CELL
        bottom = (rect.bottom - 1) // CELL

        # Check every cell touched by the player
        for r in range(top, bottom + 1):
            for c in range(left, right + 1):

                # Moving into this cell from the left
                if c > left and walls[r][c][3]:
                    return False

                # Moving into this cell from the right
                if c < right and walls[r][c][2]:
                    return False

                # Moving into this cell from above
                if r > top and walls[r][c][0]:
                    return False

                # Moving into this cell from below
                if r < bottom and walls[r][c][1]:
                    return False

        return True

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class Enemy:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c*CELL+CELL//2, r*CELL+CELL//2
        self.rect = pygame.Rect(cx-12, cy-12, 24, 24)
        self.color = (220, 60, 60)
        self.timer = 0
        self.move_interval = 30  # frames between cell moves
        self.frozen = False

    def update(self, walls, player, rows, cols):
        from game.maze import bfs
        self.timer += 1
        if self.timer >= self.move_interval:
            self.timer = 0
            pr, pc = player.rect.centery//CELL, player.rect.centerx//CELL
            step = bfs(walls, (self.r, self.c), (pr, pc), rows, cols)
            if step:
                dr, dc = step

                new_r = self.r + dr
                new_c = self.c + dc

                if 0 <= new_r < rows and 0 <= new_c < cols:
                    self.r = new_r
                    self.c = new_c

                    cx = self.c * CELL + CELL // 2
                    cy = self.r * CELL + CELL // 2
                    self.rect.center = (cx, cy)

    def draw(self, screen):
        draw_color = (80, 170, 255) if self.frozen else self.color

        pygame.draw.rect(
            screen,
            draw_color,
            self.rect,
            border_radius=5
        )

        # eyes
        for ex in [self.rect.x + 4, self.rect.x + 14]:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (ex, self.rect.y + 8),
                4
            )

            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (ex + 1, self.rect.y + 8),
                2
            )
