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


class ChargeableJump:
    def __init__(self, initial_force: int, max_force: int, step: int) -> None:
        self.step = step
        self.queued_force = 0
        self.max_force = max_force
        self.max_force_reached = False
        self.initial_force = initial_force

    def charge(self) -> None:
        if self.queued_force:
            self.queued_force = pygame.math.clamp(
                self.queued_force + self.step, self.initial_force, self.max_force
            )
        else:
            self.queued_force = self.initial_force

    def get_jump_force(self) -> int:
        return self.queued_force

    def reset(self) -> None:
        self.queued_force = 0
        self.max_force_reached = False


class Player:
    def __init__(self) -> None:
        self.width = 32
        self.height = 64
        self.speed = 300
        self.jump = ChargeableJump(900, 1800, 50)
        self.max_jump_reached = False
        self.vel = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(WIDTH / 2, FLOOR - self.height)

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
                self.jump.charge()
        elif self.jump.queued_force > 0:
            self.vel.y += self.jump.get_jump_force() * -1
            self.jump.reset()

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
