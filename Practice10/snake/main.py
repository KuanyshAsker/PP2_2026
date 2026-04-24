import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Window and grid settings
CELL_SIZE = 20
COLS = 30
ROWS = 20
TOP_MARGIN = 40
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + TOP_MARGIN

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 50, 50)
GRAY = (120, 120, 120)
YELLOW = (240, 210, 0)

# Game settings
BASE_SPEED = 8              # starting speed
FOODS_PER_LEVEL = 4         # level up after every 4 foods

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 40)


def make_walls():
    """Create border walls around the playing field."""
    walls = set()

    # Top and bottom border
    for x in range(COLS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))

    # Left and right border
    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLS - 1, y))

    return walls


def draw_cell(color, position):
    """Draw one grid cell."""
    x, y = position
    rect = pygame.Rect(
        x * CELL_SIZE,
        TOP_MARGIN + y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, color, rect)


def draw_text(text, font_obj, color, x, y):
    """Draw text on the screen."""
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


def random_food_position(snake, walls):
    """Generate food position not on snake and not on walls."""
    free_cells = []

    for x in range(COLS):
        for y in range(ROWS):
            pos = (x, y)
            if pos not in snake and pos not in walls:
                free_cells.append(pos)

    return random.choice(free_cells)


def draw_game(snake, food, walls, score, level):
    """Draw everything: HUD, walls, food, snake."""
    screen.fill(BLACK)

    # HUD
    draw_text(f"Score: {score}", font, WHITE, 10, 10)
    draw_text(f"Level: {level}", font, WHITE, WIDTH - 100, 10)

    # Walls
    for wall in walls:
        draw_cell(GRAY, wall)

    # Food
    draw_cell(RED, food)

    # Snake head
    draw_cell(YELLOW, snake[0])

    # Snake body
    for part in snake[1:]:
        draw_cell(GREEN, part)

    pygame.display.update()


def show_game_over(score, level):
    """Show game over message for a short time."""
    screen.fill(BLACK)
    text1 = big_font.render("Game Over", True, RED)
    text2 = font.render(f"Score: {score}", True, WHITE)
    text3 = font.render(f"Level: {level}", True, WHITE)

    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 30))

    pygame.display.update()
    pygame.time.wait(2500)


def main():
    # Snake starts in the middle
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)          # moving right
    next_direction = direction

    walls = make_walls()
    food = random_food_position(snake, walls)

    score = 0
    level = 1
    speed = BASE_SPEED

    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Prevent immediate reverse direction
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)

        direction = next_direction

        # New head position
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Check if snake leaves playing area
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            break

        # Check collision with wall
        if new_head in walls:
            break

        # Check if snake will eat food
        ate_food = (new_head == food)

        # Check collision with itself
        # If snake does not eat, tail moves away this turn
        body_to_check = snake if ate_food else snake[:-1]
        if new_head in body_to_check:
            break

        # Move snake
        snake.insert(0, new_head)

        if ate_food:
            score += 1
            food = random_food_position(snake, walls)

            # Level increases every few foods
            level = score // FOODS_PER_LEVEL + 1
            speed = BASE_SPEED + (level - 1) * 2
        else:
            snake.pop()

        draw_game(snake, food, walls, score, level)
        clock.tick(speed)

    show_game_over(score, level)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()