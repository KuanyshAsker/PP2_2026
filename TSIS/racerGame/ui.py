import os

import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 220, 40)
ORANGE = (255, 130, 0)
PURPLE = (130, 45, 180)
CYAN = (0, 210, 255)
DARK_GRAY = (45, 45, 45)
LIGHT_GREEN = (80, 230, 120)
INK = (18, 24, 38)
PANEL = (24, 30, 46)
PANEL_LIGHT = (36, 44, 64)
ACCENT = (255, 205, 58)
MINT = (91, 220, 168)
SKY = (83, 190, 255)
SOFT_WHITE = (241, 246, 252)


class Button:
    # Simple button object: rectangle + text + action name.
    def __init__(self, label, rect, action):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.action = action


def load_image_or_surface(resource_path, filename, size, fallback_drawer):
    # First try real PNG from resources. If missing, draw a basic fallback.
    image_path = os.path.join(resource_path, filename)

    if os.path.exists(image_path):
        loaded_image = pygame.image.load(image_path)
        return pygame.transform.scale(loaded_image, size)

    image = pygame.Surface(size, pygame.SRCALPHA)
    fallback_drawer(image)
    return image


def draw_oil_spill(surface):
    pygame.draw.ellipse(surface, (18, 18, 18), surface.get_rect())
    pygame.draw.ellipse(surface, (60, 60, 60), (8, 8, surface.get_width() - 16, surface.get_height() - 20))
    pygame.draw.arc(surface, PURPLE, (10, 8, 36, 22), 0, 3.14, 3)


def draw_road_block(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, ORANGE, surface.get_rect(), border_radius=6)
    pygame.draw.rect(surface, WHITE, (7, 8, surface.get_width() - 14, 8), border_radius=3)
    pygame.draw.rect(surface, WHITE, (7, surface.get_height() - 16, surface.get_width() - 14, 8), border_radius=3)


def draw_speed_bump(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, YELLOW, surface.get_rect(), border_radius=5)

    for x in range(-surface.get_height(), surface.get_width(), 18):
        pygame.draw.line(surface, BLACK, (x, surface.get_height()), (x + surface.get_height(), 0), 4)


def draw_nitro_strip(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, CYAN, surface.get_rect(), border_radius=5)
    pygame.draw.polygon(
        surface,
        WHITE,
        [
            (surface.get_width() // 2, 5),
            (surface.get_width() - 10, surface.get_height() // 2),
            (surface.get_width() // 2, surface.get_height() - 5),
            (10, surface.get_height() // 2),
        ],
    )


def draw_pothole(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surface, DARK_GRAY, surface.get_rect())
    pygame.draw.ellipse(surface, BLACK, (8, 6, surface.get_width() - 16, surface.get_height() - 12))
    pygame.draw.arc(surface, (95, 95, 95), (5, 4, surface.get_width() - 10, surface.get_height() - 8), 3.14, 6.2, 3)


def draw_nitro_power_up(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, CYAN, surface.get_rect().center, surface.get_width() // 2)
    pygame.draw.polygon(
        surface,
        WHITE,
        [
            (surface.get_width() // 2, 6),
            (surface.get_width() - 8, surface.get_height() // 2),
            (surface.get_width() // 2, surface.get_height() - 6),
            (8, surface.get_height() // 2),
        ],
    )


def draw_shield_power_up(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, BLUE, surface.get_rect().center, surface.get_width() // 2)
    pygame.draw.polygon(
        surface,
        WHITE,
        [
            (surface.get_width() // 2, 7),
            (surface.get_width() - 10, 14),
            (surface.get_width() - 13, surface.get_height() - 10),
            (surface.get_width() // 2, surface.get_height() - 5),
            (13, surface.get_height() - 10),
            (10, 14),
        ],
    )


def draw_repair_power_up(surface):
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, LIGHT_GREEN, surface.get_rect().center, surface.get_width() // 2)
    pygame.draw.rect(surface, WHITE, (surface.get_width() // 2 - 5, 9, 10, surface.get_height() - 18), border_radius=2)
    pygame.draw.rect(surface, WHITE, (9, surface.get_height() // 2 - 5, surface.get_width() - 18, 10), border_radius=2)


class GameUI:
    def __init__(self):
        # Keeping all fonts here so screens use the same style.
        self.font = pygame.font.SysFont("Verdana", 54, bold=True)
        self.font_mid = pygame.font.SysFont("Verdana", 24, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 18)
        self.font_tiny = pygame.font.SysFont("Verdana", 14)

    def draw_arcade_background(self, surface):
        # Background for menu screens, not the racing road itself.
        surface.fill(INK)
        for y in range(0, surface.get_height(), 28):
            color = (30, 38, 58) if (y // 28) % 2 == 0 else (23, 29, 45)
            pygame.draw.rect(surface, color, (0, y, surface.get_width(), 28))
        pygame.draw.circle(surface, (50, 62, 90), (surface.get_width() - 45, 72), 90)
        pygame.draw.circle(surface, (41, 90, 118), (45, surface.get_height() - 50), 95)

    def draw_button(self, surface, button, selected=False):
        # selected=True is used for current settings like color/difficulty.
        color = ACCENT if selected else PANEL_LIGHT
        text_color = INK if selected else SOFT_WHITE
        pygame.draw.rect(surface, (8, 12, 22), button.rect.move(0, 4), border_radius=8)
        pygame.draw.rect(surface, color, button.rect, border_radius=8)
        pygame.draw.rect(surface, SOFT_WHITE, button.rect, 2, border_radius=8)
        label = self.font_small.render(button.label, True, text_color)
        label_rect = label.get_rect(center=button.rect.center)
        surface.blit(label, label_rect)

    def make_menu_buttons(self, labels, start_y):
        # Make vertical menu buttons without repeating the same rect code.
        buttons = []
        for index, label in enumerate(labels):
            buttons.append(Button(label, (90, start_y + index * 66, 220, 46), label.lower().replace(" ", "_")))
        return buttons

    def draw_main_menu(self, surface):
        # First screen: player chooses where to go.
        self.draw_arcade_background(surface)
        title = self.font.render("Racer", True, ACCENT)
        subtitle = self.font_small.render("Arcade road rush", True, SOFT_WHITE)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 95)))
        surface.blit(subtitle, subtitle.get_rect(center=(surface.get_width() // 2, 145)))
        buttons = self.make_menu_buttons(["Play", "Leaderboard", "Settings", "Quit"], 210)
        for button in buttons:
            self.draw_button(surface, button)
        return buttons

    def draw_name_entry(self, surface, username):
        # Player name is used later for the leaderboard.
        self.draw_arcade_background(surface)
        title = self.font_mid.render("Driver Name", True, ACCENT)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 115)))
        pygame.draw.rect(surface, PANEL, (55, 175, 290, 58), border_radius=8)
        pygame.draw.rect(surface, ACCENT, (55, 175, 290, 58), 2, border_radius=8)
        name_text = self.font_mid.render(username or "Player", True, SOFT_WHITE)
        surface.blit(name_text, name_text.get_rect(center=(surface.get_width() // 2, 204)))
        hint = self.font_small.render("Press Enter to race", True, SOFT_WHITE)
        surface.blit(hint, hint.get_rect(center=(surface.get_width() // 2, 265)))
        buttons = [Button("Back", (90, 335, 220, 46), "main_menu")]
        self.draw_button(surface, buttons[0])
        return buttons

    def draw_settings_screen(self, surface, settings, car_colors, difficulties):
        # Settings are clickable and saved immediately in racer.py.
        self.draw_arcade_background(surface)
        title = self.font_mid.render("Settings", True, ACCENT)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 58)))
        buttons = []

        sound_label = "Sound: On" if settings["sound_enabled"] else "Sound: Off"
        sound_button = Button(sound_label, (62, 100, 276, 42), "toggle_sound")
        buttons.append(sound_button)
        self.draw_button(surface, sound_button, settings["sound_enabled"])

        label = self.font_small.render("Car color", True, SOFT_WHITE)
        surface.blit(label, (62, 165))
        for index, color_name in enumerate(car_colors):
            button = Button(color_name, (62 + index * 94, 195, 84, 38), f"car_{color_name}")
            buttons.append(button)
            self.draw_button(surface, button, settings["car_color"] == color_name)

        label = self.font_small.render("Difficulty", True, SOFT_WHITE)
        surface.blit(label, (62, 258))
        for index, difficulty in enumerate(difficulties):
            button = Button(difficulty, (62 + index * 94, 288, 84, 38), f"difficulty_{difficulty}")
            buttons.append(button)
            self.draw_button(surface, button, settings["difficulty"] == difficulty)

        back_button = Button("Back", (90, 420, 220, 46), "main_menu")
        buttons.append(back_button)
        self.draw_button(surface, back_button)
        return buttons

    def draw_leaderboard_screen(self, surface, leaderboard):
        # Separate leaderboard screen from the main menu.
        self.draw_arcade_background(surface)
        title = self.font_mid.render("Leaderboard", True, ACCENT)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 52)))
        self.draw_top_scores(surface, leaderboard, 95, light=True)
        back_button = Button("Back", (90, 525, 220, 46), "main_menu")
        self.draw_button(surface, back_button)
        return [back_button]

    def draw_lane_guides(self, surface, road_left, lane_width, lane_count, screen_height):
        # These lines make lanes more readable during gameplay.
        for lane_number in range(1, lane_count):
            x_position = road_left + lane_number * lane_width
            pygame.draw.line(surface, (230, 236, 245), (x_position, 0), (x_position, screen_height), 2)

    def draw_hud(
        self,
        surface,
        score,
        coins,
        enemy_speed,
        checkpoints,
        difficulty,
        distance,
        remaining_distance,
        effect_message,
        active_power_up,
        power_up_time,
    ):
        # Compact HUD so it does not cover the whole road.
        pygame.draw.rect(surface, PANEL, (10, 10, 178, 88), border_radius=8)
        pygame.draw.rect(surface, PANEL, (212, 10, 178, 88), border_radius=8)
        pygame.draw.rect(surface, ACCENT, (10, 10, 178, 88), 2, border_radius=8)
        pygame.draw.rect(surface, MINT, (212, 10, 178, 88), 2, border_radius=8)

        left_lines = [f"Score {score}", f"Coins {coins}", f"Dist {distance}m"]
        right_lines = [f"Left {remaining_distance}m", f"Diff {difficulty}", f"Cars {enemy_speed}"]

        for index, text in enumerate(left_lines):
            label = self.font_tiny.render(text, True, SOFT_WHITE)
            surface.blit(label, (20, 18 + index * 24))

        for index, text in enumerate(right_lines):
            label = self.font_tiny.render(text, True, SOFT_WHITE)
            surface.blit(label, (224, 18 + index * 24))

        power_label = active_power_up or "none"
        if power_up_time:
            power_label = f"{power_label} {power_up_time}"
        power_text = self.font_tiny.render(f"Power {power_label}", True, ACCENT)
        surface.blit(power_text, (20, 106))

        checkpoint_text = self.font_tiny.render(f"Checkpoints {checkpoints}", True, SOFT_WHITE)
        surface.blit(checkpoint_text, (224, 106))

        if effect_message:
            effect_text = self.font_small.render(effect_message, True, ACCENT)
            effect_rect = effect_text.get_rect(center=(surface.get_width() // 2, 142))
            surface.blit(effect_text, effect_rect)

    def draw_top_scores(self, surface, leaderboard, start_y, light=False):
        # Used both on leaderboard screen and end screen.
        text_color = SOFT_WHITE if light else BLACK
        muted = (180, 190, 205) if light else BLACK
        header = self.font_tiny.render("Rank  Name       Score   Dist", True, muted)
        surface.blit(header, (35, start_y))

        if not leaderboard:
            empty_text = self.font_small.render("No scores yet", True, text_color)
            surface.blit(empty_text, (35, start_y + 40))
            return

        for index, entry in enumerate(leaderboard[:10]):
            name = entry.get("name", "Player")[:8]
            score = entry.get("score", 0)
            distance = int(entry.get("distance", 0))
            row = self.font_tiny.render(
                f"{index + 1:>2}.   {name:<8} {score:>5}   {distance:>4}m",
                True,
                text_color,
            )
            surface.blit(row, (35, start_y + 28 + index * 30))

    def draw_game_over_screen(self, surface, title, stats):
        # Final run summary with buttons instead of closing instantly.
        self.draw_arcade_background(surface)
        title_text = self.font_mid.render(title, True, ACCENT)
        surface.blit(title_text, title_text.get_rect(center=(surface.get_width() // 2, 80)))

        panel = pygame.Rect(45, 135, 310, 150)
        pygame.draw.rect(surface, PANEL, panel, border_radius=8)
        pygame.draw.rect(surface, ACCENT, panel, 2, border_radius=8)
        lines = [
            f"Score: {stats['score']}",
            f"Distance: {stats['distance']}m",
            f"Coins: {stats['coins']}",
        ]
        for index, text in enumerate(lines):
            label = self.font_small.render(text, True, SOFT_WHITE)
            surface.blit(label, (70, 158 + index * 38))

        buttons = [
            Button("Retry", (90, 345, 220, 46), "retry"),
            Button("Main Menu", (90, 410, 220, 46), "main_menu"),
        ]
        for button in buttons:
            self.draw_button(surface, button)
        return buttons
