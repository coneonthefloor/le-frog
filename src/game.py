import pygame

WIDTH = 1280
HEIGHT = 720

FLOOR = HEIGHT - 100
GRAVITY = 100

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0


class Player:
    def __init__(self) -> None:
        self.width = 32
        self.height = 64
        self.speed = 300
        self.jump_force = 900
        self.jump_multiplier = 130
        self.max_jump_force = 10
        self.jump_count = 0
        self.max_jump_reached = False
        self.vel = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(WIDTH / 2, FLOOR - self.height)

    def jump(self) -> None:
        self.vel.y += self.jump_force * -1

    def grounded(self) -> bool:
        return self.pos.y + self.height == FLOOR

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        if not self.grounded():
            self.vel.y += GRAVITY

        if self.pos.y + self.height > FLOOR:
            self.vel.y = 0
            self.pos.y = FLOOR - self.height

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            if self.grounded():
                self.jump()
                self.max_jump_reached = False
                self.jump_count = 0
            elif self.vel.y < 0 and not self.max_jump_reached:
                self.jump_count += 1
                self.vel.y = self.vel.y - self.jump_multiplier
                if self.jump_count == self.max_jump_force:
                    self.max_jump_reached = True


    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, "white", (*self.pos, self.width, self.height))


player = Player()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")

    player.update(dt)
    player.draw(screen)

    pygame.draw.rect(screen, "white", (0, FLOOR, WIDTH, HEIGHT - FLOOR))

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
