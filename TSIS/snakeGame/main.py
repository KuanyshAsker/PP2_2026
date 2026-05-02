import pygame
import random
import sys
from pathlib import Path

from db import (
    DatabaseError,
    get_personal_best,
    get_top_scores,
    init_db,
    save_game_session
)
from config import load_preferences, save_preferences

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
DARK_RED = (120, 20, 30)
GRAY = (105, 110, 120)
YELLOW = (240, 210, 0)
ORANGE = (255, 150, 0)
PURPLE = (160, 80, 220)
BLUE = (70, 130, 255)
BUTTON = (35, 43, 63)
BUTTON_HOVER = (52, 64, 92)
BUTTON_BORDER = (105, 120, 155)
INPUT_BG = (11, 15, 25)
SUCCESS = (80, 220, 130)

# Game settings
BASE_SPEED = 8              # starting snake speed
FOODS_PER_LEVEL = 4         # level up after every 4 score points
FOOD_LIFETIME = 5000        # food disappears after 5000 milliseconds = 5 seconds
POISON_SHRINK = 2           # poison removes 2 snake segments
# Power-ups use ms because pygame ticks also speak in ms.
POWERUP_FIELD_LIFETIME = 8000
POWERUP_EFFECT_DURATION = 5000
POWERUP_MIN_SPAWN_DELAY = 4000
POWERUP_MAX_SPAWN_DELAY = 9000
OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL = 4
OBSTACLE_MAX_ATTEMPTS = 250

# Asset paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Verdana", 18)
small_font = pygame.font.SysFont("Verdana", 13)
medium_font = pygame.font.SysFont("Verdana", 24, bold=True)
big_font = pygame.font.SysFont("Verdana", 44)
GAME_PREFERENCES = load_preferences()


def load_powerup_images():
    """Load and scale power-up icons from the assets folder."""
    image_files = {
        "speed": "SpeedBoost.png",
        "slow": "SlowMotion.png",
        "shield": "Shield.png"
    }
    images = {}

    for kind, filename in image_files.items():
        path = ASSETS_DIR / filename

        try:
            image = pygame.image.load(str(path)).convert_alpha()
            images[kind] = pygame.transform.smoothscale(image, (CELL_SIZE, CELL_SIZE))
        except (FileNotFoundError, pygame.error):
            images[kind] = None

    return images


POWERUP_IMAGES = load_powerup_images()


def clean_username(username):
    """Prepare a typed username for database storage."""
    return username.strip()[:50]


def setup_database():
    """Create database tables and return a status tuple for the UI."""
    # If db is down, game still runs, just without saving scores.
    try:
        init_db()
        return True, "Database connected"
    except DatabaseError as error:
        return False, f"DB offline: {error}"


def load_personal_best(username, db_ready):
    """Safely load the user's best score."""
    if not db_ready:
        return 0

    try:
        return get_personal_best(username)
    except DatabaseError:
        return 0


def save_result(username, score, level, db_ready):
    """Save a completed game and return text for the game over screen."""
    if not db_ready:
        return "Result not saved: database is offline"

    try:
        save_game_session(username, score, level)
        return "Result saved"
    except DatabaseError as error:
        return f"Result not saved: {error}"


class Food:
    """Food object with random position, weight, color, and timer."""

    def __init__(self, snake, walls, blocked_positions=None):
        self.respawn(snake, walls, blocked_positions)

    def respawn(self, snake, walls, blocked_positions=None):
        """Create new food in a random free cell."""
        # Weight means how many points the food gives.
        # Weight 1 is common, weight 2 is less common, weight 3 is rare.
        self.weight = random.choices(
            [1, 2, 3],
            weights=[60, 30, 10],
            k=1
        )[0]
        # Rare 3-point fruit is chunky, so it takes 2x2 cells.
        self.size = 2 if self.weight == 3 else 1
        self.position = random_food_position(snake, walls, blocked_positions, self.size)

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

    def cells(self):
        """Return every cell occupied by this food."""
        x, y = self.position
        cells = []

        for offset_x in range(self.size):
            for offset_y in range(self.size):
                cells.append((x + offset_x, y + offset_y))

        return cells


class PoisonFood:
    """Poison item that shortens the snake when eaten."""

    def __init__(self, snake, walls, blocked_positions=None):
        self.color = DARK_RED
        self.respawn(snake, walls, blocked_positions)

    def respawn(self, snake, walls, blocked_positions=None):
        """Create poison in a random free cell."""
        self.position = random_food_position(snake, walls, blocked_positions)


class PowerUp:
    """Temporary power-up item that appears on the field."""

    # Short ids are easier to compare in the main loop.
    TYPES = ("speed", "slow", "shield")
    COLORS = {
        "speed": YELLOW,
        "slow": BLUE,
        "shield": SUCCESS
    }
    NAMES = {
        "speed": "Speed boost",
        "slow": "Slow motion",
        "shield": "Shield"
    }

    def __init__(self):
        self.kind = None
        self.position = None
        self.spawn_time = 0
        self.next_spawn_time = pygame.time.get_ticks() + random.randint(
            POWERUP_MIN_SPAWN_DELAY,
            POWERUP_MAX_SPAWN_DELAY
        )

    def is_on_field(self):
        """Return True if a power-up is currently visible."""
        return self.position is not None

    def spawn(self, snake, walls, blocked_positions=None):
        """Place one random power-up on a free field cell."""
        self.kind = random.choice(self.TYPES)
        self.position = random_food_position(snake, walls, blocked_positions)
        self.spawn_time = pygame.time.get_ticks()

    def clear(self, delay=True):
        """Remove the power-up from the field."""
        self.kind = None
        self.position = None
        self.spawn_time = 0

        if delay:
            self.next_spawn_time = pygame.time.get_ticks() + random.randint(
                POWERUP_MIN_SPAWN_DELAY,
                POWERUP_MAX_SPAWN_DELAY
            )

    def is_expired(self):
        """Check whether the visible power-up has timed out."""
        if not self.is_on_field():
            return False

        return pygame.time.get_ticks() - self.spawn_time >= POWERUP_FIELD_LIFETIME

    def should_spawn(self):
        """Check whether the next power-up should appear."""
        return not self.is_on_field() and pygame.time.get_ticks() >= self.next_spawn_time


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


def neighbors(position):
    """Return the four grid neighbors of a position."""
    x, y = position
    return [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]


def reachable_area_size(start, blocked):
    """Count how many free cells can be reached from start."""
    if start in blocked:
        return 0

    visited = {start}
    queue = [start]

    while queue:
        current = queue.pop(0)

        for next_pos in neighbors(current):
            x, y = next_pos

            if x < 0 or x >= COLS or y < 0 or y >= ROWS:
                continue

            if next_pos in visited or next_pos in blocked:
                continue

            visited.add(next_pos)
            queue.append(next_pos)

    return len(visited)


def position_is_safe_for_snake(snake, walls, obstacles):
    """Check that new obstacles do not trap the snake head."""
    head = snake[0]
    blocked = set(walls) | set(obstacles) | set(snake[1:])
    open_neighbors = 0

    for next_pos in neighbors(head):
        if next_pos not in blocked:
            open_neighbors += 1

    if open_neighbors == 0:
        return False

    return reachable_area_size(head, blocked) >= max(12, len(snake) + 6)


def make_obstacles(level, snake, walls, blocked_positions=None):
    """Randomly place internal obstacle blocks for the current level."""
    if level < OBSTACLE_START_LEVEL:
        return set()

    obstacles = set()
    blocked = set(blocked_positions or [])
    blocked.update(snake)
    blocked.update(walls)

    head_x, head_y = snake[0]
    safe_zone = set()
    # Keep some breathing room near the head, otherwise lvl-up feels unfair.
    for x in range(head_x - 2, head_x + 3):
        for y in range(head_y - 2, head_y + 3):
            safe_zone.add((x, y))

    target_count = min(OBSTACLES_PER_LEVEL * (level - 2), 36)
    attempts = 0

    while len(obstacles) < target_count and attempts < OBSTACLE_MAX_ATTEMPTS:
        attempts += 1
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))

        if pos in blocked or pos in obstacles or pos in safe_zone:
            continue

        candidate = set(obstacles)
        candidate.add(pos)

        if position_is_safe_for_snake(snake, walls, candidate):
            obstacles = candidate

    return obstacles


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


def draw_toggle(rect, label, enabled):
    """Draw a settings toggle."""
    draw_button(rect, f"{label}: {'ON' if enabled else 'OFF'}")


def draw_input_box(rect, text, active=True, placeholder="Type username..."):
    """Draw a username input box."""
    border_color = BLUE if active else BORDER
    pygame.draw.rect(screen, INPUT_BG, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

    shown_text = text if text else placeholder
    text_color = WHITE if text else GRAY
    draw_text(shown_text, font, text_color, rect.x + 14, rect.y + 15)


def short_status(text, max_chars=72):
    """Keep status text inside the game window."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."


def draw_main_menu(username, message, start_button, leaderboard_button, settings_button, quit_button):
    """Draw the start screen with username entry."""
    screen.fill(BG)

    title = big_font.render("Snake", True, HEAD)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 44))

    subtitle = small_font.render("Enter username to start", True, GRAY)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 96))

    input_rect = pygame.Rect(WIDTH // 2 - 180, 136, 360, 54)
    draw_input_box(input_rect, username)

    draw_button(start_button, "Play")
    draw_button(leaderboard_button, "Leaderboard")
    draw_button(settings_button, "Settings")
    draw_button(quit_button, "Quit")

    status_color = SUCCESS if message == "Database connected" else GRAY
    status_text = small_font.render(short_status(message), True, status_color)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 48))

    hint = small_font.render("Press Enter to play, click Settings, Esc to quit", True, GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 25))

    pygame.display.update()


def show_main_menu(db_ready, db_status):
    """Ask the player for a username before the game starts."""
    username = ""
    message = db_status
    start_button = pygame.Rect(WIDTH // 2 - 90, 210, 180, 44)
    leaderboard_button = pygame.Rect(WIDTH // 2 - 90, 268, 180, 44)
    settings_button = pygame.Rect(WIDTH // 2 - 90, 326, 180, 44)
    quit_button = pygame.Rect(WIDTH // 2 - 90, 384, 180, 44)

    while True:
        draw_main_menu(username, message, start_button, leaderboard_button, settings_button, quit_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cleaned = clean_username(username)
                    if cleaned:
                        personal_best = load_personal_best(cleaned, db_ready)
                        return cleaned, personal_best
                    message = "Enter a username first"

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                elif event.unicode and event.unicode.isprintable() and len(username) < 50:
                    username += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    cleaned = clean_username(username)
                    if cleaned:
                        personal_best = load_personal_best(cleaned, db_ready)
                        return cleaned, personal_best
                    message = "Enter a username first"

                if leaderboard_button.collidepoint(event.pos):
                    show_leaderboard(db_ready, db_status)

                if settings_button.collidepoint(event.pos):
                    show_settings_screen()

                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        clock.tick(60)


def draw_leaderboard_screen(rows, message, back_button):
    """Draw Top 10 leaderboard rows."""
    screen.fill(BG)

    title = medium_font.render("Top 10 Scores", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    table = pygame.Rect(50, 78, WIDTH - 100, 340)
    pygame.draw.rect(screen, HUD_BG, table, border_radius=18)
    pygame.draw.rect(screen, BORDER, table, 2, border_radius=18)

    headers = ["#", "Player", "Score", "Level", "Date"]
    header_x = [72, 122, 318, 418, 500]
    for index, label in enumerate(headers):
        draw_text(label, small_font, GRAY, header_x[index], 100)

    if rows:
        for index, row in enumerate(rows, start=1):
            username, score, level_reached, played_at = row
            y = 108 + index * 28
            date_text = played_at.strftime("%Y-%m-%d") if hasattr(played_at, "strftime") else str(played_at)[:10]

            draw_text(str(index), small_font, WHITE, header_x[0], y)
            draw_text(short_status(username, 16), small_font, WHITE, header_x[1], y)
            draw_text(str(score), small_font, WHITE, header_x[2], y)
            draw_text(str(level_reached), small_font, WHITE, header_x[3], y)
            draw_text(date_text, small_font, WHITE, header_x[4], y)
    else:
        empty = font.render("No saved games yet", True, GRAY)
        screen.blit(empty, (WIDTH // 2 - empty.get_width() // 2, table.centery - 12))

    draw_button(back_button, "Back")

    status = small_font.render(short_status(message), True, GRAY)
    screen.blit(status, (WIDTH // 2 - status.get_width() // 2, HEIGHT - 30))

    pygame.display.update()


def show_leaderboard(db_ready, db_status):
    """Open the leaderboard screen until the player goes back."""
    rows = []
    message = db_status

    if db_ready:
        try:
            rows = get_top_scores(10)
        except DatabaseError as error:
            message = f"Could not load leaderboard: {error}"

    back_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 86, 140, 44)

    while True:
        draw_leaderboard_screen(rows, message, back_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN):
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    return

        clock.tick(60)


def clamp_color_value(text):
    """Convert RGB text input to a valid color value."""
    if text == "":
        return 0

    return max(0, min(255, int(text)))


def update_preferences_color(preferences, rgb_text):
    """Update temporary RGB preferences from input text."""
    preferences["snake_color"] = [
        clamp_color_value(rgb_text["r"]),
        clamp_color_value(rgb_text["g"]),
        clamp_color_value(rgb_text["b"])
    ]


def draw_settings_screen(preferences, rgb_text, active_channel, rects):
    """Draw the settings screen."""
    screen.fill(BG)

    title = medium_font.render("Settings", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    color_label = font.render("Snake color", True, WHITE)
    screen.blit(color_label, (82, 96))

    preview_color = tuple(preferences["snake_color"])
    pygame.draw.rect(screen, preview_color, pygame.Rect(82, 132, 70, 44), border_radius=10)
    pygame.draw.rect(screen, BORDER, pygame.Rect(82, 132, 70, 44), 2, border_radius=10)

    channel_labels = {"r": "R", "g": "G", "b": "B"}
    for channel in ["r", "g", "b"]:
        box = rects[channel]
        draw_text(channel_labels[channel], small_font, GRAY, box.x, box.y - 20)
        draw_input_box(box, rgb_text[channel], active_channel == channel, placeholder="0")

    draw_toggle(rects["grid"], "Grid overlay", preferences["grid_overlay"])
    draw_toggle(rects["sound"], "Sound", preferences["sound"])
    draw_button(rects["save"], "Save & Back")

    hint = small_font.render("Click R/G/B boxes and type 0-255. Press Esc to cancel.", True, GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 34))

    pygame.display.update()


def show_settings_screen():
    """Let the user edit preferences saved in settings.json."""
    # Edit a copy first; real settings save only on Save & Back.
    preferences = {
        "snake_color": list(GAME_PREFERENCES["snake_color"]),
        "grid_overlay": GAME_PREFERENCES["grid_overlay"],
        "sound": GAME_PREFERENCES["sound"]
    }
    rgb_text = {
        "r": str(preferences["snake_color"][0]),
        "g": str(preferences["snake_color"][1]),
        "b": str(preferences["snake_color"][2])
    }
    active_channel = None
    rects = {
        "r": pygame.Rect(190, 132, 78, 44),
        "g": pygame.Rect(288, 132, 78, 44),
        "b": pygame.Rect(386, 132, 78, 44),
        "grid": pygame.Rect(WIDTH // 2 - 130, 222, 260, 44),
        "sound": pygame.Rect(WIDTH // 2 - 130, 284, 260, 44),
        "save": pygame.Rect(WIDTH // 2 - 90, 374, 180, 44)
    }

    while True:
        draw_settings_screen(preferences, rgb_text, active_channel, rects)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    GAME_PREFERENCES.update(preferences)
                    save_preferences(GAME_PREFERENCES)
                    return

                if active_channel is not None:
                    if event.key == pygame.K_BACKSPACE:
                        rgb_text[active_channel] = rgb_text[active_channel][:-1]
                        update_preferences_color(preferences, rgb_text)
                    elif event.unicode.isdigit() and len(rgb_text[active_channel]) < 3:
                        rgb_text[active_channel] += event.unicode
                        rgb_text[active_channel] = str(clamp_color_value(rgb_text[active_channel]))
                        update_preferences_color(preferences, rgb_text)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                active_channel = None

                for channel in ["r", "g", "b"]:
                    if rects[channel].collidepoint(event.pos):
                        active_channel = channel

                if rects["grid"].collidepoint(event.pos):
                    preferences["grid_overlay"] = not preferences["grid_overlay"]

                if rects["sound"].collidepoint(event.pos):
                    preferences["sound"] = not preferences["sound"]

                if rects["save"].collidepoint(event.pos):
                    GAME_PREFERENCES.update(preferences)
                    save_preferences(GAME_PREFERENCES)
                    return

        clock.tick(60)


def random_food_position(snake, walls, blocked_positions=None, size=1):
    """Generate item position that is not on the snake, walls, or blocked cells."""
    free_cells = []
    blocked = set(blocked_positions or [])

    for x in range(COLS - size + 1):
        for y in range(ROWS - size + 1):
            item_cells = []

            for offset_x in range(size):
                for offset_y in range(size):
                    item_cells.append((x + offset_x, y + offset_y))

            can_place = True
            for pos in item_cells:
                if pos in snake or pos in walls or pos in blocked:
                    can_place = False
                    break

            if can_place:
                free_cells.append((x, y))

    return random.choice(free_cells)


def draw_hud(
    score,
    level,
    food,
    personal_best,
    active_speed_effect=None,
    speed_effect_end_time=0,
    shield_charges=0
):
    """Draw the top user interface with score, timer, and level."""
    pygame.draw.rect(screen, HUD_BG, (0, 0, WIDTH, TOP_MARGIN))

    # Four compact HUD cards
    score_box = pygame.Rect(12, 14, 120, 54)
    timer_box = pygame.Rect(140, 14, 210, 54)
    level_box = pygame.Rect(358, 14, 104, 54)
    best_box = pygame.Rect(470, 14, 178, 54)

    for box in [score_box, timer_box, level_box, best_box]:
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

    draw_text("PERSONAL BEST", small_font, GRAY, best_box.x + 14, best_box.y + 8)
    draw_text(str(personal_best), medium_font, WHITE, best_box.x + 14, best_box.y + 24)

    current_time = pygame.time.get_ticks()
    if shield_charges > 0:
        draw_text("POWER-UP: Shield ready", small_font, SUCCESS, 14, 70)
    elif active_speed_effect is not None and current_time < speed_effect_end_time:
        seconds_left = (speed_effect_end_time - current_time) // 1000 + 1
        label = PowerUp.NAMES[active_speed_effect]
        draw_text(f"POWER-UP: {label} {seconds_left}s", small_font, SUCCESS, 14, 70)


def draw_grid():
    """Draw a subtle grid inside the play area."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID, (x, TOP_MARGIN), (x, HEIGHT))

    for y in range(TOP_MARGIN, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def draw_food(food):
    """Draw food and show its weight number."""
    if food.size == 2:
        x, y = food.position
        food_rect = pygame.Rect(
            x * CELL_SIZE + 2,
            TOP_MARGIN + y * CELL_SIZE + 2,
            CELL_SIZE * 2 - 4,
            CELL_SIZE * 2 - 4
        )
        pygame.draw.rect(screen, food.color, food_rect, border_radius=10)
    else:
        draw_cell(food.color, food.position, radius=7, padding=2)

    x, y = food.position
    text = small_font.render(str(food.weight), True, WHITE)
    text_x = x * CELL_SIZE + (CELL_SIZE * food.size) // 2 - text.get_width() // 2
    text_y = TOP_MARGIN + y * CELL_SIZE + (CELL_SIZE * food.size) // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))


def draw_poison(poison):
    """Draw poison food with a distinct dark red marker."""
    draw_cell(poison.color, poison.position, radius=7, padding=2)

    x, y = poison.position
    text = small_font.render("X", True, WHITE)
    text_x = x * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
    text_y = TOP_MARGIN + y * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))


def darker_color(color):
    """Return a darker shade of an RGB color."""
    return (
        max(0, int(color[0] * 0.65)),
        max(0, int(color[1] * 0.65)),
        max(0, int(color[2] * 0.65))
    )


def draw_powerup(powerup):
    """Draw the active field power-up, if there is one."""
    if not powerup.is_on_field():
        return

    image = POWERUP_IMAGES.get(powerup.kind)
    rect = cell_rect(powerup.position, padding=1)

    pygame.draw.rect(
        screen,
        PowerUp.COLORS[powerup.kind],
        rect,
        border_radius=7
    )

    if image is not None:
        screen.blit(image, rect)
    else:
        label = powerup.kind[0].upper()
        text = small_font.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


def draw_snake(snake, direction):
    """Draw the snake body and a simple face on the head."""
    # Snake color comes from settings.json, so the player can style it.
    snake_color = tuple(GAME_PREFERENCES["snake_color"])
    snake_dark = darker_color(snake_color)

    # Body
    for index, part in enumerate(snake[1:]):
        shade = snake_color if index % 2 == 0 else snake_dark
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


def draw_game(
    snake,
    food,
    poison,
    powerup,
    walls,
    obstacles,
    score,
    level,
    direction,
    personal_best,
    active_speed_effect=None,
    speed_effect_end_time=0,
    shield_charges=0
):
    """Draw everything: HUD, play area, grid, walls, food, and snake."""
    screen.fill(BG)
    draw_hud(
        score,
        level,
        food,
        personal_best,
        active_speed_effect,
        speed_effect_end_time,
        shield_charges
    )

    # Play area
    pygame.draw.rect(screen, PLAY_BG, PLAY_RECT)
    if GAME_PREFERENCES["grid_overlay"]:
        draw_grid()
    pygame.draw.rect(screen, BORDER, PLAY_RECT, 3)

    # Draw walls
    for wall in walls:
        draw_cell((80, 85, 95), wall, radius=3, padding=1)

    for obstacle in obstacles:
        draw_cell((115, 105, 85), obstacle, radius=4, padding=1)

    draw_food(food)
    draw_poison(poison)
    draw_powerup(powerup)
    draw_snake(snake, direction)

    pygame.display.update()


def draw_game_over_screen(username, score, level, personal_best, save_message, retry_button, menu_button):
    """Draw the game over menu with Retry and Main Menu buttons."""
    screen.fill(BG)

    # Main card
    card = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 165, 420, 330)
    pygame.draw.rect(screen, HUD_BG, card, border_radius=22)
    pygame.draw.rect(screen, BORDER, card, 3, border_radius=22)

    title = big_font.render("Game Over", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, card.y + 38))

    player_text = font.render(f"Player: {username}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    best_text = font.render(f"Personal Best: {personal_best}", True, WHITE)
    save_text = small_font.render(short_status(save_message, 46), True, GRAY)
    hint_text = small_font.render("Press R to retry or M for main menu", True, GRAY)

    screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, card.y + 98))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, card.y + 128))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, card.y + 158))
    screen.blit(best_text, (WIDTH // 2 - best_text.get_width() // 2, card.y + 188))
    screen.blit(save_text, (WIDTH // 2 - save_text.get_width() // 2, card.y + 220))
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, card.y + 242))

    draw_button(retry_button, "Retry")
    draw_button(menu_button, "Main Menu")

    pygame.display.update()


def show_game_over(username, score, level, personal_best, save_message):
    """
    Show game over screen until the user chooses Retry or Main Menu.

    Returns:
        "retry" if the player wants to restart
        "menu" if the player wants to return to the main menu
    """
    retry_button = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 105, 140, 46)
    menu_button = pygame.Rect(WIDTH // 2 - 5, HEIGHT // 2 + 105, 175, 46)

    while True:
        draw_game_over_screen(
            username,
            score,
            level,
            personal_best,
            save_message,
            retry_button,
            menu_button
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    return "retry"
                if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                    return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_button.collidepoint(event.pos):
                    return "retry"
                if menu_button.collidepoint(event.pos):
                    return "menu"

        clock.tick(60)


def item_blockers(food, poison, powerup=None):
    """Return cells occupied by visible non-snake items."""
    blocked = set(food.cells())
    blocked.add(poison.position)

    if powerup is not None and powerup.is_on_field():
        blocked.add(powerup.position)

    return blocked


def get_current_speed(base_speed, active_speed_effect, effect_end_time):
    """Apply temporary speed power-up effects to the current game speed."""
    current_time = pygame.time.get_ticks()

    if current_time >= effect_end_time:
        return base_speed

    if active_speed_effect == "speed":
        return base_speed + 5

    if active_speed_effect == "slow":
        return max(3, base_speed - 4)

    return base_speed


def activate_powerup(
    powerup,
    current_time,
    active_speed_effect,
    speed_effect_end_time,
    shield_charges
):
    """Return updated effect state after collecting a power-up."""
    if powerup.kind == "speed":
        active_speed_effect = "speed"
        speed_effect_end_time = current_time + POWERUP_EFFECT_DURATION
    elif powerup.kind == "slow":
        active_speed_effect = "slow"
        speed_effect_end_time = current_time + POWERUP_EFFECT_DURATION
    elif powerup.kind == "shield":
        shield_charges = 1

    return active_speed_effect, speed_effect_end_time, shield_charges


def run_game(personal_best):
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
    obstacles = set()
    food = Food(snake, walls)
    poison = PoisonFood(snake, walls, blocked_positions=food.cells())
    powerup = PowerUp()

    score = 0
    level = 1
    speed = BASE_SPEED
    extra_growth = 0
    active_speed_effect = None
    speed_effect_end_time = 0
    shield_charges = 0

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
        current_time = pygame.time.get_ticks()
        solid_walls = walls | obstacles

        if current_time >= speed_effect_end_time:
            active_speed_effect = None

        if powerup.is_expired():
            powerup.clear()

        if powerup.should_spawn():
            powerup.spawn(snake, solid_walls, blocked_positions=item_blockers(food, poison))

        # If food timer ended, remove old food and create new food
        if food.is_expired():
            blocked_positions = {poison.position}
            if powerup.is_on_field():
                blocked_positions.add(powerup.position)

            food.respawn(snake, solid_walls, blocked_positions=blocked_positions)

        # Calculate new snake head position
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Check if snake hits the wall border
        if new_head in solid_walls:
            if shield_charges > 0:
                # Shield tanks this bad move once, then it's gone.
                shield_charges -= 1
                current_best = max(personal_best, score)
                draw_game(
                    snake,
                    food,
                    poison,
                    powerup,
                    walls,
                    obstacles,
                    score,
                    level,
                    direction,
                    current_best,
                    active_speed_effect,
                    speed_effect_end_time,
                    shield_charges
                )
                clock.tick(get_current_speed(speed, active_speed_effect, speed_effect_end_time))
                continue

            running = False
            continue

        ate_food = (new_head in food.cells())
        ate_poison = (new_head == poison.position)
        ate_powerup = powerup.is_on_field() and new_head == powerup.position

        # If the tail will move away, do not count it as collision.
        if ate_food or (extra_growth > 0 and not ate_poison):
            body_to_check = snake
        else:
            body_to_check = snake[:-1]

        # Check collision with itself
        if new_head in body_to_check:
            if shield_charges > 0:
                # Same idea for self-hit: one free save, no more.
                shield_charges -= 1
                current_best = max(personal_best, score)
                draw_game(
                    snake,
                    food,
                    poison,
                    powerup,
                    walls,
                    obstacles,
                    score,
                    level,
                    direction,
                    current_best,
                    active_speed_effect,
                    speed_effect_end_time,
                    shield_charges
                )
                clock.tick(get_current_speed(speed, active_speed_effect, speed_effect_end_time))
                continue

            running = False
            continue

        # Move snake by adding new head
        snake.insert(0, new_head)

        if ate_powerup:
            active_speed_effect, speed_effect_end_time, shield_charges = activate_powerup(
                powerup,
                current_time,
                active_speed_effect,
                speed_effect_end_time,
                shield_charges
            )
            powerup.clear()

        if ate_food:
            score += food.weight
            extra_growth += food.weight - 1
            blocked_positions = {poison.position}
            if powerup.is_on_field():
                blocked_positions.add(powerup.position)

            new_level = score // FOODS_PER_LEVEL + 1
            if new_level != level:
                level = new_level
                # New level, new arena layout. Keeps the game spicy.
                obstacles = make_obstacles(
                    level,
                    snake,
                    walls,
                    blocked_positions=item_blockers(food, poison, powerup)
                )

            solid_walls = walls | obstacles
            food.respawn(snake, solid_walls, blocked_positions=blocked_positions)
            speed = BASE_SPEED + (level - 1) * 2

        elif ate_poison:
            snake.pop()
            extra_growth = max(0, extra_growth - POISON_SHRINK)

            for _ in range(POISON_SHRINK):
                if len(snake) > 1:
                    snake.pop()

            if len(snake) <= 1:
                running = False
                continue

            blocked_positions = set(food.cells())
            if powerup.is_on_field():
                blocked_positions.add(powerup.position)

            poison.respawn(snake, solid_walls, blocked_positions=blocked_positions)

        elif extra_growth > 0:
            extra_growth -= 1

        else:
            snake.pop()

        current_best = max(personal_best, score)
        draw_game(
            snake,
            food,
            poison,
            powerup,
            walls,
            obstacles,
            score,
            level,
            direction,
            current_best,
            active_speed_effect,
            speed_effect_end_time,
            shield_charges
        )
        clock.tick(get_current_speed(speed, active_speed_effect, speed_effect_end_time))

    return score, level


def main():
    """Main program loop with menu, gameplay, and game over screens."""
    db_ready, db_status = setup_database()

    # Outer loop = menu loop. Inner loop = retry same player.
    while True:
        username, personal_best = show_main_menu(db_ready, db_status)

        while True:
            score, level = run_game(personal_best)
            save_message = save_result(username, score, level, db_ready)
            personal_best = max(personal_best, score)
            choice = show_game_over(username, score, level, personal_best, save_message)

            if choice == "menu":
                break

            # If the user chooses retry, the loop starts a new round.


if __name__ == "__main__":
    main()
