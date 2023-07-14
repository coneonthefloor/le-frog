import os
import pygame

WIDTH = 1280
HEIGHT = 720

FLOOR = HEIGHT - 100
GRAVITY = 50

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0


class Animation:
    def __init__(self, frames: list[pygame.Surface], frame_rate: int) -> None:
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame_index = 0
        self.last_tick = pygame.time.get_ticks()

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_tick >= self.frame_rate:
            self.last_tick = current_time
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.current_frame_index = 0

    def enter(self):
        self.current_frame_index = 0
        self.last_tick = pygame.time.get_ticks()

    def exit(self):
        self.current_frame_index = 0

    def get_current_frame(self) -> pygame.Surface:
        return self.frames[self.current_frame_index]


class SpriteSheet:
    def __init__(self, image_path: str, cell_width: int, cell_height: int) -> None:
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path)
        self.sprites: list[list[pygame.Surface]] = []
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.cols = self.image.get_width() // self.cell_width
        self.rows = self.image.get_height() // self.cell_height
        self.generate_sprites()

    def generate_sprites(self) -> None:
        cell_size = (self.cell_height, self.cell_height)
        for row_index in range(0, self.rows):
            row = []
            for col_index in range(0, self.cols):
                sprite = pygame.Surface(cell_size, pygame.SRCALPHA)
                sprite.set_colorkey("white")
                x = col_index * self.cell_width
                y = row_index * self.cell_height
                sprite.blit(self.image, (0, 0), (x, y, *cell_size))
                row.append(sprite)
            self.sprites.append(row)

    def get_sprite(self, row: int, col: int) -> pygame.Surface:
        return self.sprites[row][col]

    def get_sprite_scaled(
        self, row: int, col: int, scale_x: float, scale_y: float
    ) -> pygame.Surface:
        sprite = self.get_sprite(row, col)
        sprite_scaled = pygame.transform.scale_by(sprite, (scale_x, scale_y))
        return sprite_scaled.convert_alpha()


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
    def __init__(self, sprite_sheet: SpriteSheet) -> None:
        self.width = 32
        self.height = 64
        self.speed = 300
        self.scale = (4, 4)
        self.sprite_sheet = sprite_sheet
        self.sprites = []
        for col in range(0, self.sprite_sheet.cols):
            self.sprites.append(
                self.sprite_sheet.get_sprite_scaled(0, col, *self.scale)
            )
        self.falling_frame = 4
        self.jumping_frame = 3
        self.charging_jump = 2
        self.idle_frame = 0
        self.current_frame = 0
        self.walking = False
        self.walking_animation = Animation(
            [self.sprites[1], self.sprites[2]], 250
        )
        self.jump = ChargeableJump(900, 1800, 50)
        self.vel = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(WIDTH / 2, FLOOR - self.height)
        self.facing_right = True

    def grounded(self) -> bool:
        return self.pos.y + self.height == FLOOR

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt

        if not self.grounded():
            self.vel.y += GRAVITY

        self.vel.y = pygame.math.clamp(self.vel.y, -self.jump.max_force, 700)
        if self.pos.y + self.height > FLOOR:
            self.vel.y = 0
            self.pos.y = FLOOR - self.height
        if self.pos.x > WIDTH - self.width // 2:
            self.pos.x = -self.width // 2
        if self.pos.x + self.width < -self.width // 2:
            self.pos.x = WIDTH - self.width // 2

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.grounded():
                self.jump.charge()
        elif self.jump.queued_force > 0:
            self.vel.y += self.jump.get_jump_force() * -1
            self.jump.reset()
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -self.speed if not self.vel.y else -self.speed // 2
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            self.vel.x = self.speed if not self.vel.y else self.speed // 2

        if self.vel.x and not self.vel.y and not self.walking:
            self.walking_animation.enter()
            self.walking = True

        if self.vel.y and self.walking or not self.vel.x:
            self.walking = False
            self.walking_animation.exit()

        if self.walking:
            self.walking_animation.update()

        if (
            not keys[pygame.K_RIGHT]
            and not keys[pygame.K_d]
            and not keys[pygame.K_LEFT]
            and not keys[pygame.K_a]
            or keys[pygame.K_UP]
            or keys[pygame.K_w]
        ):
            self.vel.x = 0

        if self.vel.y < 0:
            self.current_frame = self.jumping_frame
        elif self.vel.y > 0:
            self.current_frame = self.falling_frame
        elif self.jump.queued_force > 0:
            self.current_frame = self.charging_jump
        else:
            self.current_frame = self.idle_frame

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self.sprites[self.current_frame]
        if self.walking:
            sprite = self.walking_animation.get_current_frame()
        surface.blit(pygame.transform.flip(sprite, self.facing_right, False), self.pos)


character_sprites = SpriteSheet(os.path.join("assets", "characters.png"), 16, 16)
player = Player(character_sprites)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")

    player.update(dt)
    player.draw(screen)

    pygame.draw.rect(screen, "grey", (0, FLOOR, WIDTH, HEIGHT - FLOOR))

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
