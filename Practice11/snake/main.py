import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Window and grid settings
CELL_SIZE = 22
COLS = 30
ROWS = 20
TOP_MARGIN = 86
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + TOP_MARGIN
PLAY_RECT = pygame.Rect(0, TOP_MARGIN, WIDTH, ROWS * CELL_SIZE)

# Colors
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
BG = (12, 15, 24)
PLAY_BG = (4, 7, 12)
HUD_BG = (21, 26, 39)
HUD_BOX = (31, 38, 55)
GRID = (20, 26, 38)
BORDER = (70, 80, 105)
GREEN = (0, 210, 90)
DARK_GREEN = (0, 135, 65)
HEAD = (245, 215, 45)
RED = (230, 65, 75)
GRAY = (105, 110, 120)
YELLOW = (240, 210, 0)
ORANGE = (255, 150, 0)
PURPLE = (160, 80, 220)
BLUE = (70, 130, 255)
BUTTON = (35, 43, 63)
BUTTON_HOVER = (52, 64, 92)
BUTTON_BORDER = (105, 120, 155)

# Game settings
BASE_SPEED = 8              # starting snake speed
FOODS_PER_LEVEL = 4         # level up after every 4 score points
FOOD_LIFETIME = 5000        # food disappears after 5000 milliseconds = 5 seconds

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Verdana", 18)
small_font = pygame.font.SysFont("Verdana", 13)
medium_font = pygame.font.SysFont("Verdana", 24, bold=True)
big_font = pygame.font.SysFont("Verdana", 44)


class Food:
    """Food object with random position, weight, color, and timer."""

    def __init__(self, snake, walls):
        self.respawn(snake, walls)

    def respawn(self, snake, walls):
        """Create new food in a random free cell."""
        self.position = random_food_position(snake, walls)

        # Weight means how many points the food gives.
        # Weight 1 is common, weight 2 is less common, weight 3 is rare.
        self.weight = random.choices(
            [1, 2, 3],
            weights=[60, 30, 10],
            k=1
        )[0]

        if self.weight == 1:
            self.color = RED
        elif self.weight == 2:
            self.color = ORANGE
        else:
            self.color = PURPLE

        self.spawn_time = pygame.time.get_ticks()

    def time_left(self):
        """Return how many milliseconds are left before food disappears."""
        current_time = pygame.time.get_ticks()
        passed_time = current_time - self.spawn_time
        return max(0, FOOD_LIFETIME - passed_time)

    def is_expired(self):
        """Check if food has stayed on screen too long."""
        return self.time_left() <= 0


def make_walls():
    """Create border walls around the playing field."""
    walls = set()

    for x in range(COLS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))

    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLS - 1, y))

    return walls


def cell_rect(position, padding=1):
    """Return the pygame rectangle for one grid cell."""
    x, y = position
    return pygame.Rect(
        x * CELL_SIZE + padding,
        TOP_MARGIN + y * CELL_SIZE + padding,
        CELL_SIZE - padding * 2,
        CELL_SIZE - padding * 2
    )


def draw_cell(color, position, radius=5, padding=1):
    """Draw one rounded grid cell."""
    pygame.draw.rect(screen, color, cell_rect(position, padding), border_radius=radius)


def draw_text(text, font_obj, color, x, y):
    """Draw text on the screen."""
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


def draw_text_center(text, font_obj, color, rect):
    """Draw text centered inside a rectangle."""
    img = font_obj.render(text, True, color)
    img_rect = img.get_rect(center=rect.center)
    screen.blit(img, img_rect)


def draw_button(rect, label):
    """Draw a rounded button and return True if the mouse is hovering over it."""
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER if hovered else BUTTON

    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2, border_radius=12)
    draw_text_center(label, font, WHITE, rect)

    return hovered


def random_food_position(snake, walls):
    """Generate food position that is not on the snake and not on walls."""
    free_cells = []

    for x in range(COLS):
        for y in range(ROWS):
            pos = (x, y)
            if pos not in snake and pos not in walls:
                free_cells.append(pos)

    return random.choice(free_cells)


def draw_hud(score, level, food):
    """Draw the top user interface with score, timer, and level."""
    pygame.draw.rect(screen, HUD_BG, (0, 0, WIDTH, TOP_MARGIN))

    # Three clean HUD cards
    score_box = pygame.Rect(14, 14, 165, 54)
    timer_box = pygame.Rect(WIDTH // 2 - 105, 14, 210, 54)
    level_box = pygame.Rect(WIDTH - 179, 14, 165, 54)

    for box in [score_box, timer_box, level_box]:
        pygame.draw.rect(screen, HUD_BOX, box, border_radius=14)
        pygame.draw.rect(screen, BORDER, box, 2, border_radius=14)

    draw_text("SCORE", small_font, GRAY, score_box.x + 14, score_box.y + 8)
    draw_text(str(score), medium_font, WHITE, score_box.x + 14, score_box.y + 24)

    draw_text("FOOD TIMER", small_font, GRAY, timer_box.x + 14, timer_box.y + 8)
    seconds_left = food.time_left() // 1000 + 1
    draw_text(f"{seconds_left}s", medium_font, WHITE, timer_box.x + 14, timer_box.y + 24)

    # Timer progress bar
    bar_x = timer_box.x + 78
    bar_y = timer_box.y + 33
    bar_w = 112
    bar_h = 10
    ratio = food.time_left() / FOOD_LIFETIME
    pygame.draw.rect(screen, (55, 60, 75), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
    pygame.draw.rect(screen, BLUE, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=5)

    draw_text("LEVEL", small_font, GRAY, level_box.x + 14, level_box.y + 8)
    draw_text(str(level), medium_font, WHITE, level_box.x + 14, level_box.y + 24)


def draw_grid():
    """Draw a subtle grid inside the play area."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID, (x, TOP_MARGIN), (x, HEIGHT))

    for y in range(TOP_MARGIN, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def draw_food(food):
    """Draw food and show its weight number."""
    draw_cell(food.color, food.position, radius=7, padding=2)

    x, y = food.position
    text = small_font.render(str(food.weight), True, WHITE)
    text_x = x * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
    text_y = TOP_MARGIN + y * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))


def draw_snake(snake, direction):
    """Draw the snake body and a simple face on the head."""
    # Body
    for index, part in enumerate(snake[1:]):
        shade = GREEN if index % 2 == 0 else DARK_GREEN
        draw_cell(shade, part, radius=6, padding=1)

    # Head
    draw_cell(HEAD, snake[0], radius=7, padding=1)

    # Small eyes on the head make the snake feel more alive
    head_rect = cell_rect(snake[0], padding=1)
    dx, dy = direction

    if dx == 1:       # moving right
        eye1 = (head_rect.centerx + 4, head_rect.centery - 4)
        eye2 = (head_rect.centerx + 4, head_rect.centery + 4)
    elif dx == -1:    # moving left
        eye1 = (head_rect.centerx - 4, head_rect.centery - 4)
        eye2 = (head_rect.centerx - 4, head_rect.centery + 4)
    elif dy == -1:    # moving up
        eye1 = (head_rect.centerx - 4, head_rect.centery - 4)
        eye2 = (head_rect.centerx + 4, head_rect.centery - 4)
    else:             # moving down
        eye1 = (head_rect.centerx - 4, head_rect.centery + 4)
        eye2 = (head_rect.centerx + 4, head_rect.centery + 4)

    pygame.draw.circle(screen, BLACK, eye1, 2)
    pygame.draw.circle(screen, BLACK, eye2, 2)


def draw_game(snake, food, walls, score, level, direction):
    """Draw everything: HUD, play area, grid, walls, food, and snake."""
    screen.fill(BG)
    draw_hud(score, level, food)

    # Play area
    pygame.draw.rect(screen, PLAY_BG, PLAY_RECT)
    draw_grid()
    pygame.draw.rect(screen, BORDER, PLAY_RECT, 3)

    # Draw walls
    for wall in walls:
        draw_cell((80, 85, 95), wall, radius=3, padding=1)

    draw_food(food)
    draw_snake(snake, direction)

    pygame.display.update()


def draw_game_over_screen(score, level, retry_button, quit_button):
    """Draw the game over menu with Retry and Quit buttons."""
    screen.fill(BG)

    # Main card
    card = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 165, 420, 330)
    pygame.draw.rect(screen, HUD_BG, card, border_radius=22)
    pygame.draw.rect(screen, BORDER, card, 3, border_radius=22)

    title = big_font.render("Game Over", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, card.y + 38))

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    hint_text = small_font.render("Press R to retry or Q to quit", True, GRAY)

    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, card.y + 115))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, card.y + 148))
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, card.y + 184))

    draw_button(retry_button, "Retry")
    draw_button(quit_button, "Quit")

    pygame.display.update()


def show_game_over(score, level):
    """
    Show game over screen until the user chooses Retry or Quit.

    Returns:
        "retry" if the player wants to restart
        "quit" if the player wants to close the game
    """
    retry_button = pygame.Rect(WIDTH // 2 - 145, HEIGHT // 2 + 75, 130, 46)
    quit_button = pygame.Rect(WIDTH // 2 + 15, HEIGHT // 2 + 75, 130, 46)

    while True:
        draw_game_over_screen(score, level, retry_button, quit_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    return "retry"
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_button.collidepoint(event.pos):
                    return "retry"
                if quit_button.collidepoint(event.pos):
                    return "quit"

        clock.tick(60)


def run_game():
    """
    Run one round of the game.

    This function returns score and level when the player loses.
    The program does not quit here, because the game over menu decides
    whether the user wants to retry or quit.
    """
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    next_direction = direction

    walls = make_walls()
    food = Food(snake, walls)

    score = 0
    level = 1
    speed = BASE_SPEED
    extra_growth = 0

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Prevent the snake from immediately reversing direction
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)

        direction = next_direction

        # If food timer ended, remove old food and create new food
        if food.is_expired():
            food.respawn(snake, walls)

        # Calculate new snake head position
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Check if snake hits the wall border
        if new_head in walls:
            running = False
            continue

        ate_food = (new_head == food.position)

        # If the tail will move away, do not count it as collision.
        if ate_food or extra_growth > 0:
            body_to_check = snake
        else:
            body_to_check = snake[:-1]

        # Check collision with itself
        if new_head in body_to_check:
            running = False
            continue

        # Move snake by adding new head
        snake.insert(0, new_head)

        if ate_food:
            score += food.weight
            extra_growth += food.weight - 1
            food.respawn(snake, walls)

            level = score // FOODS_PER_LEVEL + 1
            speed = BASE_SPEED + (level - 1) * 2

        elif extra_growth > 0:
            extra_growth -= 1

        else:
            snake.pop()

        draw_game(snake, food, walls, score, level, direction)
        clock.tick(speed)

    return score, level


def main():
    """Main game loop. Lets the user retry after losing."""
    while True:
        score, level = run_game()
        choice = show_game_over(score, level)

        if choice == "quit":
            pygame.quit()
            sys.exit()

        # If the user chooses retry, the loop starts a new round.


if __name__ == "__main__":
    main()
