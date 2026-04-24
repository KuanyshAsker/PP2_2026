# Imports
import pygame, sys, os
from pygame.locals import *
import random, time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game settings
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS = 0

# Resources folder
RESOURCE_PATH = "resources"

# Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load images
background = pygame.image.load(os.path.join(RESOURCE_PATH, "AnimatedStreet.png"))

# Load and play background music
pygame.mixer.music.load(os.path.join(RESOURCE_PATH, "background.wav"))
pygame.mixer.music.set_volume(0.5)   # optional volume
pygame.mixer.music.play(-1)          # -1 means loop forever

# Create window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(RESOURCE_PATH, "Enemy.png"))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        # Reset enemy after leaving screen
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(RESOURCE_PATH, "Coin.png"))
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # Spawn coin above the screen randomly
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-600, -50)
        )

    def move(self):
        self.rect.move_ip(0, SPEED)

        # Respawn coin after leaving screen
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(RESOURCE_PATH, "Player.png"))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # Move left
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        # Move right
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


# Create sprites
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Sprite groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins_group = pygame.sprite.Group()
coins_group.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(C1)
all_sprites.add(E1)
all_sprites.add(P1)

# Increase speed every second
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # Show score
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # Show collected coins in top right
    coins_text = font_small.render(f"Coins: {COINS}", True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coins_text, coins_rect)

    # Draw and move sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Collect coin
    collected_coin = pygame.sprite.spritecollideany(P1, coins_group)
    if collected_coin:
        COINS += 1
        collected_coin.reset()

    # Collision with enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.music.stop()  # stop background music
        pygame.mixer.Sound(os.path.join(RESOURCE_PATH, "crash.wav")).play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)