import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.exit_font = pygame.font.SysFont("monospace", 10)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.hud_font = pygame.font.SysFont("monospace", 16)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)
        self.enemies = [
            Enemy(0, COLS - 1),
            Enemy(ROWS - 1, 0),
            Enemy(ROWS - 1, COLS - 1)
        ]

        pellet_r = ROWS // 2
        pellet_c = COLS // 2 - 2

        self.pellet_rect = pygame.Rect(
            pellet_c * CELL + CELL // 2 - 7,
            pellet_r * CELL + CELL // 2 - 7,
            14,
            14
        )

        self.pellet_collected = False
        self.freeze_end_time = 0
        self.exit_rect = pygame.Rect((COLS//2)*CELL+5, (ROWS//2)*CELL+5, CELL-10, CELL-10)
        self.caught = False
        self.won = False
        self.start_time = pygame.time.get_ticks()
        self.speed_tier = 0
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
        return True

    def update(self):
        if self.caught or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # Existing Task 2 speed system
        elapsed = pygame.time.get_ticks() - self.start_time
        current_tier = elapsed // 15000

        if current_tier > self.speed_tier:
            for enemy in self.enemies:
                enemy.move_interval = max(5, enemy.move_interval - 2)

            self.speed_tier = current_tier

        # Power pellet collision
        if not self.pellet_collected and self.player.rect.colliderect(self.pellet_rect):
            self.pellet_collected = True
            self.freeze_end_time = pygame.time.get_ticks() + 5000

            for enemy in self.enemies:
                enemy.frozen = True

        if (
            self.pellet_collected
            and self.freeze_end_time > 0
            and pygame.time.get_ticks() >= self.freeze_end_time
        ):
            for enemy in self.enemies:
                enemy.frozen = False

            self.freeze_end_time = 0

        for enemy in self.enemies:
            if not enemy.frozen:
                enemy.update(self.walls, self.player, ROWS, COLS)

        # Existing collision detection
        for enemy in self.enemies:
            if not enemy.frozen and self.player.rect.colliderect(enemy.rect):
                self.caught = True
                break

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True
        if not self.caught and not self.won:
            self.score += 1

    def draw(self):
        self.screen.fill((230, 220, 210))
        wc=(50,40,60)
        for r in range(ROWS):
            for c in range(COLS):
                x,y=c*CELL,r*CELL
                w=self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen,wc,(x,y),(x+CELL,y),3)
                if w[1]: pygame.draw.line(self.screen,wc,(x,y+CELL),(x+CELL,y+CELL),3)
                if w[2]: pygame.draw.line(self.screen,wc,(x+CELL,y),(x+CELL,y+CELL),3)
                if w[3]: pygame.draw.line(self.screen,wc,(x,y),(x,y+CELL),3)
        pygame.draw.rect(self.screen,(80,200,80),self.exit_rect,border_radius=4)
        lbl = self.exit_font.render("EXIT", True, (20,80,20))
        self.screen.blit(lbl, (self.exit_rect.x+5, self.exit_rect.y+8))
        if not self.pellet_collected:
            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                self.pellet_rect.center,
                7
            )
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        hud=pygame.Rect(0,ROWS*CELL,WIDTH,50)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)

        info = self.hud_font.render(
            f"Survived: {self.score // 60}s    Speed Tier: {self.speed_tier}    R=Restart",
            True,
            (200, 200, 200)
        )
        self.screen.blit(info, (8, ROWS * CELL + 17))
        if self.caught:
            self._overlay("CAUGHT!", (220,60,60))
        if self.won:
            self._overlay("ESCAPED!", (80,220,80))
        pygame.display.flip()

    def _overlay(self, text, color):
        surf=pygame.Surface((WIDTH,ROWS*CELL),pygame.SRCALPHA)
        surf.fill((0,0,0,140))
        self.screen.blit(surf,(0,0))
        msg=self.big_font.render(text,True,color)
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,ROWS*CELL//2-30))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,ROWS*CELL//2+20))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
