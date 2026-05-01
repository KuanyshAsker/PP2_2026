# Imports
import pygame
import sys
import os
import random
import time
from pygame.locals import *


# Initialize pygame
pygame.init()
pygame.mixer.init()


# Game settings
FPS = 60
FramePerSec = pygame.time.Clock()


# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Road boundaries where enemies and coins can appear
ROAD_LEFT = 40
ROAD_RIGHT = SCREEN_WIDTH - 40

# Player, enemy, and coin settings
PLAYER_SPEED = 5
ENEMY_SPEED = 5
COIN_SPEED = 5

# Game counters
SCORE = 0
COINS = 0

# Enemy speed will increase after every N collected coins
N = 5
LAST_SPEED_UP_COINS = 0


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
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


# Create window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load enemy image
        self.image = pygame.image.load(os.path.join(RESOURCE_PATH, "Enemy.png"))
        self.rect = self.image.get_rect()

        # Place enemy at a random x position at the top of the road
        self.reset()

    def reset(self):
        # Reset enemy position to the top of the screen
        self.rect.center = (
            random.randint(ROAD_LEFT, ROAD_RIGHT),
            0
        )

    def move(self):
        global SCORE

        # Move enemy down using enemy speed
        self.rect.move_ip(0, ENEMY_SPEED)

        # If enemy leaves the screen, increase score and respawn enemy
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load original coin image
        self.original_image = pygame.image.load(os.path.join(RESOURCE_PATH, "Coin.png"))

        # Coin value will be set inside reset()
        self.value = 1

        # Spawn coin for the first time
        self.reset()

    def reset(self):
        # Randomly choose coin value.
        # The list [1, 2, 3] means coins can have different weights.
        # The weights [60, 30, 10] mean:
        # value 1 coin is common,
        # value 2 coin is less common,
        # value 3 coin is rare.
        self.value = random.choices(
            [1, 2, 3],
            weights=[60, 30, 10],
            k=1
        )[0]

        # Change coin size depending on value
        if self.value == 1:
            size = 30
        elif self.value == 2:
            size = 40
        else:
            size = 50

        # Scale coin image based on its value
        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.rect = self.image.get_rect()

        # Spawn coin above the screen at a random x position on the road
        self.rect.center = (
            random.randint(ROAD_LEFT, ROAD_RIGHT),
            random.randint(-700, -50)
        )

    def move(self):
        # Move coin down the screen
        self.rect.move_ip(0, COIN_SPEED)

        # If coin leaves the screen, respawn it
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load player image
        self.image = pygame.image.load(os.path.join(RESOURCE_PATH, "Player.png"))
        self.rect = self.image.get_rect()

        # Starting position of the player
        self.rect.center = (160, 520)

    def move(self):
        # Get pressed keyboard keys
        pressed_keys = pygame.key.get_pressed()

        # Move player left
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)

        # Move player right
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)


# Create sprites
P1 = Player()
E1 = Enemy()

# Create several coins so they appear randomly on the road
coins_group = pygame.sprite.Group()
for i in range(3):
    coin = Coin()
    coins_group.add(coin)

# Enemy group
enemies = pygame.sprite.Group()
enemies.add(E1)

# Group containing all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(coins_group)


# Main game loop
while True:
    for event in pygame.event.get():
        # Quit the game
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # Show score
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # Show collected coins
    coins_text = font_small.render(f"Coins: {COINS}", True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coins_text, coins_rect)

    # Show current enemy speed
    speed_text = font_small.render(f"Enemy speed: {ENEMY_SPEED}", True, BLACK)
    DISPLAYSURF.blit(speed_text, (10, 35))

    # Draw and move all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Check if player collected any coin
    collected_coins = pygame.sprite.spritecollide(P1, coins_group, False)

    for coin in collected_coins:
        # Add coin value to total coins
        COINS += coin.value

        # Respawn collected coin
        coin.reset()

    # Increase enemy speed when player earns every N coins
    if COINS - LAST_SPEED_UP_COINS >= N:
        ENEMY_SPEED += 1
        LAST_SPEED_UP_COINS = COINS

    # Check collision between player and enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        # Stop background music
        pygame.mixer.music.stop()

        # Play crash sound
        pygame.mixer.Sound(os.path.join(RESOURCE_PATH, "crash.wav")).play()
        time.sleep(0.5)

        # Show game over screen
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        # Remove all sprites
        for entity in all_sprites:
            entity.kill()

        # Wait and close game
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Update display
    pygame.display.update()

    # Control FPS
    FramePerSec.tick(FPS)