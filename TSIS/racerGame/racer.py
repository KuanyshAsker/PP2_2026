import os
import random
import sys
import time

import pygame
from pygame.locals import K_BACKSPACE, K_ESCAPE, K_LEFT, K_RETURN, K_RIGHT, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from persistence import add_leaderboard_entry, load_leaderboard, load_settings, save_settings
from ui import (
    GameUI,
    load_image_or_surface,
    draw_nitro_power_up,
    draw_nitro_strip,
    draw_oil_spill,
    draw_pothole,
    draw_repair_power_up,
    draw_road_block,
    draw_shield_power_up,
    draw_speed_bump,
)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CAR_COLOR_TINTS = {
    "Blue": (90, 190, 255),
    "Red": (255, 85, 95),
    "Green": (92, 225, 145),
}
DIFFICULTY_MULTIPLIERS = {
    "Easy": 0.85,
    "Normal": 1.0,
    "Hard": 1.25,
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_PATH = os.path.join(BASE_DIR, "resources")


# Sprite classes below are the objects that move on the road.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, lane_index=None, y_position=-100):
        super().__init__()
        self.game = game
        self.image = game.enemy_image.copy()
        self.rect = self.image.get_rect()
        self.lane_index = lane_index
        self.place(lane_index, y_position)

    def place(self, lane_index=None, y_position=-100):
        if lane_index is None:
            lane_index = random.randrange(self.game.lane_count)

        self.lane_index = lane_index
        self.rect.center = (self.game.lane_centers[lane_index], y_position)

    def move(self):
        # Traffic goes down. If player avoids it, score counter increases.
        self.rect.move_ip(0, self.game.enemy_speed)

        if self.rect.top > self.game.screen_height:
            self.game.traffic_score += 1
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.original_image = pygame.image.load(os.path.join(RESOURCE_PATH, "Coin.png"))
        self.value = 1
        self.reset()

    def reset(self):
        # Coins have different values, so bigger coins are worth more.
        self.value = random.choices(
            [1, 2, 3],
            weights=[60, 30, 10],
            k=1,
        )[0]

        if self.value == 1:
            size = 30
        elif self.value == 2:
            size = 40
        else:
            size = 50

        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (
            random.choice(self.game.lane_centers),
            random.randint(-700, -50),
        )

    def move(self):
        self.rect.move_ip(0, self.game.coin_speed)

        if self.rect.top > self.game.screen_height:
            self.reset()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game, power_up_type, image, lane_index, y_position):
        super().__init__()
        self.game = game
        self.power_up_type = power_up_type
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (game.lane_centers[lane_index], y_position)
        self.spawn_time = pygame.time.get_ticks()

    def move(self):
        # Power-ups do not stay forever, player has to grab them fast.
        self.rect.move_ip(0, self.game.track_object_speed)

        timed_out = pygame.time.get_ticks() - self.spawn_time >= self.game.power_up_timeout

        if timed_out or self.rect.top > self.game.screen_height:
            self.kill()


class TrackObject(pygame.sprite.Sprite):
    def __init__(self, game, image, lane_index, y_position):
        super().__init__()
        self.game = game
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (game.lane_centers[lane_index], y_position)
        self.used = False

    def move(self):
        # Base movement for obstacles and road events.
        self.rect.move_ip(0, self.game.track_object_speed)

        if self.rect.top > self.game.screen_height:
            self.kill()


class OilSpill(TrackObject):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, game.oil_image, lane_index, y_position)
        self.effect_name = "Oil spill"
        self.effect_speed = game.slowed_player_speed
        self.effect_duration = 1700


class RoadBlock(TrackObject):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, game.barrier_image, lane_index, y_position)


class SpeedBump(TrackObject):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, game.speed_bump_image, lane_index, y_position)
        self.effect_name = "Speed bump"
        self.effect_speed = game.slowed_player_speed
        self.effect_duration = 1200


class Pothole(TrackObject):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, game.pothole_image, lane_index, y_position)
        self.effect_name = "Pothole"
        self.effect_speed = game.slowed_player_speed
        self.effect_duration = 1500


class NitroStrip(TrackObject):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, game.nitro_image, lane_index, y_position)
        self.effect_name = "Nitro boost"
        self.effect_speed = game.boosted_player_speed
        self.effect_duration = 2200


class MovingBarrier(RoadBlock):
    def __init__(self, game, lane_index, y_position):
        super().__init__(game, lane_index, y_position)
        self.horizontal_speed = random.choice([-2, 2])

    def move(self):
        # This one is more dangerous because it also slides sideways.
        self.rect.move_ip(self.horizontal_speed, self.game.track_object_speed)

        if self.rect.left <= self.game.road_left or self.rect.right >= self.game.road_right:
            self.horizontal_speed *= -1

        if self.rect.top > self.game.screen_height:
            self.kill()


class CheckpointLine(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((game.road_width, 8), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        for x in range(0, game.road_width, 28):
            color = WHITE if (x // 28) % 2 == 0 else BLACK
            pygame.draw.rect(self.image, color, (x, 0, 28, 8))

        self.rect = self.image.get_rect(topleft=(game.road_left, -20))
        self.scored = False

    def move(self):
        # Checkpoints are visual progress markers.
        self.rect.move_ip(0, self.game.track_object_speed)

        if self.rect.top > self.game.screen_height:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.player_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        # Player can only move left and right inside the road.
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.rect.left = max(self.game.road_left, self.rect.left - self.game.player_speed)

        if pressed_keys[K_RIGHT]:
            self.rect.right = min(self.game.road_right, self.rect.right + self.game.player_speed)


class RacerGame:
    # Main controller class: screens, gameplay loop, settings, and saving.
    def __init__(self):
        pygame.init()
        self.mixer_ready = self.init_mixer()

        self.settings = load_settings()
        self.screen = "menu"
        self.buttons = []
        self.username_input = ""
        self.last_run_stats = None
        self.result_saved = False
        self.screen_width = self.settings["screen_width"]
        self.screen_height = self.settings["screen_height"]
        self.fps = self.settings["fps"]
        self.clock = pygame.time.Clock()

        self.road_left = 40
        self.road_right = self.screen_width - 40
        self.road_width = self.road_right - self.road_left
        self.lane_count = 4
        self.lane_width = self.road_width // self.lane_count
        self.lane_centers = [
            self.road_left + self.lane_width // 2 + i * self.lane_width
            for i in range(self.lane_count)
        ]

        self.base_player_speed = self.settings["player_speed"]
        self.player_speed = self.base_player_speed
        self.boosted_player_speed = 8
        self.slowed_player_speed = 3
        self.enemy_speed = self.settings["enemy_speed"]
        self.enemy_speed_bonus = 0
        self.coin_speed = self.settings["coin_speed"]
        self.track_object_speed = self.settings["track_object_speed"]

        self.username = "Player"
        self.score = 0
        self.traffic_score = 0
        self.coins = 0
        self.distance_traveled = 0
        self.race_distance = self.settings["race_distance"]
        self.power_up_bonus = 0
        self.checkpoints_count = 0
        self.difficulty_level = 1
        self.coins_needed_for_speed_up = 5
        self.last_speed_up_coins = 0
        self.speed_effect_end_time = 0
        self.speed_effect_message = ""
        self.active_power_up = None
        self.active_power_up_end_time = 0
        self.shield_charges = 0
        self.minimum_spawn_gap = 95
        self.base_traffic_delay = self.settings["base_traffic_delay"]
        self.base_obstacle_delay = self.settings["base_obstacle_delay"]
        self.base_power_up_delay = self.settings["base_power_up_delay"]
        self.power_up_timeout = self.settings["power_up_timeout"]
        self.max_traffic_cars = 2

        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Racer")
        self.ui = GameUI()
        self.load_assets()
        self.apply_settings()
        self.start_music()

    def init_mixer(self):
        # Audio can fail on some computers, so keep game playable anyway.
        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def load_assets(self):
        # Load all images once, then sprites reuse them.
        self.background = pygame.image.load(os.path.join(RESOURCE_PATH, "AnimatedStreet.png"))
        self.player_original_image = pygame.image.load(os.path.join(RESOURCE_PATH, "Player.png"))
        self.player_image = self.player_original_image.copy()
        self.enemy_image = pygame.image.load(os.path.join(RESOURCE_PATH, "Enemy.png"))
        self.oil_image = load_image_or_surface(RESOURCE_PATH, "OilSpill.png", (58, 34), draw_oil_spill)
        self.barrier_image = load_image_or_surface(RESOURCE_PATH, "Barrier.png", (64, 36), draw_road_block)
        self.speed_bump_image = load_image_or_surface(RESOURCE_PATH, "SpeedBump.png", (70, 24), draw_speed_bump)
        self.nitro_image = load_image_or_surface(RESOURCE_PATH, "NitroStrip.png", (70, 26), draw_nitro_strip)
        self.pothole_image = load_image_or_surface(RESOURCE_PATH, "Pothole.png", (62, 38), draw_pothole)
        self.power_up_images = {
            "Nitro": load_image_or_surface(RESOURCE_PATH, "NitroStrip.png", (38, 38), draw_nitro_power_up),
            "Shield": load_image_or_surface(RESOURCE_PATH, "Shield.png", (38, 38), draw_shield_power_up),
            "Repair": load_image_or_surface(RESOURCE_PATH, "Repair.png", (38, 38), draw_repair_power_up),
        }

    def start_music(self):
        # Respect the sound setting before playing background music.
        if not self.mixer_ready:
            return

        if not self.settings["sound_enabled"]:
            pygame.mixer.music.stop()
            return

        pygame.mixer.music.load(os.path.join(RESOURCE_PATH, "background.wav"))
        pygame.mixer.music.set_volume(self.settings["music_volume"])
        pygame.mixer.music.play(-1)

    def tint_player_image(self, color_name):
        # Blue uses original image. Other colors recolor only the car body.
        if color_name == "Blue":
            self.player_image = self.player_original_image.copy()
            return

        tint = CAR_COLOR_TINTS.get(color_name, CAR_COLOR_TINTS["Blue"])
        image = self.player_original_image.copy()

        for x in range(image.get_width()):
            for y in range(image.get_height()):
                red, green, blue, alpha = image.get_at((x, y))

                if alpha == 0:
                    continue

                is_blue_body = blue > red * 1.15 and blue > green * 1.05 and red + green + blue > 130

                if is_blue_body:
                    brightness = (red + green + blue) / 765
                    shade = 0.62 + brightness * 0.35
                    image.set_at(
                        (x, y),
                        (
                            min(255, int(tint[0] * shade)),
                            min(255, int(tint[1] * shade)),
                            min(255, int(tint[2] * shade)),
                            alpha,
                        ),
                    )

        self.player_image = image

    def apply_settings(self):
        # Called whenever user changes settings, so changes apply immediately.
        self.settings = save_settings(self.settings)
        self.difficulty_multiplier = DIFFICULTY_MULTIPLIERS.get(self.settings["difficulty"], 1.0)
        self.tint_player_image(self.settings["car_color"])

        if self.mixer_ready:
            if self.settings["sound_enabled"]:
                pygame.mixer.music.set_volume(self.settings["music_volume"])
                if not pygame.mixer.music.get_busy():
                    self.start_music()
            else:
                pygame.mixer.music.stop()

        if hasattr(self, "player"):
            center = self.player.rect.center
            self.player.image = self.player_image.copy()
            self.player.rect = self.player.image.get_rect(center=center)

    def reset_run_state(self):
        # Reset only the race data, not saved settings or leaderboard.
        self.score = 0
        self.traffic_score = 0
        self.coins = 0
        self.distance_traveled = 0
        self.power_up_bonus = 0
        self.checkpoints_count = 0
        self.difficulty_level = 1
        self.enemy_speed_bonus = 0
        self.last_speed_up_coins = 0
        self.speed_effect_end_time = 0
        self.speed_effect_message = ""
        self.active_power_up = None
        self.active_power_up_end_time = 0
        self.shield_charges = 0
        self.result_saved = False
        self.last_run_stats = None
        self.base_player_speed = self.settings["player_speed"]
        self.player_speed = self.base_player_speed
        self.enemy_speed = self.settings["enemy_speed"]
        self.coin_speed = self.settings["coin_speed"]
        self.track_object_speed = self.settings["track_object_speed"]
        self.race_distance = self.settings["race_distance"]
        self.base_traffic_delay = self.settings["base_traffic_delay"]
        self.base_obstacle_delay = self.settings["base_obstacle_delay"]
        self.base_power_up_delay = self.settings["base_power_up_delay"]
        self.power_up_timeout = self.settings["power_up_timeout"]
        self.create_sprites()
        self.schedule_first_events()

    def create_sprites(self):
        # New sprite groups are created for each new run.
        self.player = Player(self)

        self.coins_group = pygame.sprite.Group()
        for i in range(3):
            self.coins_group.add(Coin(self))

        self.enemies = pygame.sprite.Group()
        self.lethal_hazards = pygame.sprite.Group()
        self.slow_zones = pygame.sprite.Group()
        self.nitro_strips = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.checkpoints = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.coins_group)

    def schedule_first_events(self):
        # Timers decide when cars, obstacles, power-ups, etc. appear.
        current_time = pygame.time.get_ticks()
        self.next_traffic_time = current_time + 900
        self.next_obstacle_time = current_time + 1400
        self.next_power_up_time = current_time + 3600
        self.next_hazard_wave_time = current_time + 2600
        self.next_road_event_time = current_time + 2600
        self.next_checkpoint_time = current_time + 4200

    def add_track_sprite(self, sprite, *groups):
        # Add sprite to all_sprites plus its special collision group.
        self.all_sprites.add(sprite)

        for group in groups:
            group.add(sprite)

    def calculate_score(self):
        # Final score mixes distance, coins, avoided traffic and power-ups.
        return (
            int(self.distance_traveled) // 10
            + self.coins * 10
            + self.traffic_score * 25
            + self.power_up_bonus
        )

    def get_remaining_distance(self):
        # Do not allow negative distance after finish line.
        return max(0, self.race_distance - int(self.distance_traveled))

    def update_distance(self):
        # Distance increases every frame based on road speed.
        self.distance_traveled = min(
            self.race_distance,
            self.distance_traveled + self.track_object_speed * 0.08,
        )
        self.score = self.calculate_score()

    def update_difficulty(self):
        # As player survives longer, game slowly gets more busy.
        progress = self.traffic_score + self.checkpoints_count * 2 + self.coins // 3
        self.difficulty_level = min(10, 1 + progress // 6)
        self.max_traffic_cars = min(7, 1 + self.difficulty_level)
        base_enemy_speed = self.settings["enemy_speed"] + self.enemy_speed_bonus + self.difficulty_level // 2
        base_track_speed = self.settings["track_object_speed"] + self.difficulty_level // 3
        self.enemy_speed = max(2, int(base_enemy_speed * self.difficulty_multiplier))
        self.track_object_speed = max(2, int(base_track_speed * self.difficulty_multiplier))

    def get_traffic_delay(self):
        return max(420, int((self.base_traffic_delay - self.difficulty_level * 130) / self.difficulty_multiplier))

    def get_obstacle_delay(self):
        return max(580, int((self.base_obstacle_delay - self.difficulty_level * 150) / self.difficulty_multiplier))

    def get_power_up_delay(self):
        return max(3200, self.base_power_up_delay - self.difficulty_level * 120)

    def get_player_lane(self):
        player_center_x = self.player.rect.centerx
        closest_lane = 0
        closest_distance = abs(player_center_x - self.lane_centers[0])

        for lane_index, lane_center in enumerate(self.lane_centers):
            distance = abs(player_center_x - lane_center)

            if distance < closest_distance:
                closest_lane = lane_index
                closest_distance = distance

        return closest_lane

    def get_spawn_blockers(self):
        blockers = pygame.sprite.Group()
        blockers.add(self.enemies)
        blockers.add(self.lethal_hazards)
        blockers.add(self.slow_zones)
        blockers.add(self.nitro_strips)
        blockers.add(self.power_ups)
        return blockers

    def is_spawn_safe(self, image, lane_index, y_position):
        # Prevent unfair spawns on top of the player or another object.
        spawn_rect = image.get_rect(center=(self.lane_centers[lane_index], y_position))
        player_safe_rect = self.player.rect.inflate(28, 170)

        if spawn_rect.colliderect(player_safe_rect):
            return False

        for sprite in self.get_spawn_blockers():
            if spawn_rect.inflate(0, self.minimum_spawn_gap).colliderect(sprite.rect):
                return False

        return True

    def find_safe_lane(self, image, y_position, avoid_player_lane=False):
        # Try lanes in random order and take the first safe one.
        lane_choices = list(range(self.lane_count))
        random.shuffle(lane_choices)

        if avoid_player_lane and len(lane_choices) > 1:
            player_lane = self.get_player_lane()
            lane_choices = [lane for lane in lane_choices if lane != player_lane] + [player_lane]

        for lane_index in lane_choices:
            if self.is_spawn_safe(image, lane_index, y_position):
                return lane_index

        return None

    def spawn_traffic_car(self):
        # Adds one traffic car if density limit allows it.
        if len(self.enemies) >= self.max_traffic_cars:
            return

        y_position = random.randint(-170, -95)
        lane_index = self.find_safe_lane(self.enemy_image, y_position, avoid_player_lane=True)

        if lane_index is None:
            return

        traffic_car = Enemy(self, lane_index, y_position)
        self.all_sprites.add(traffic_car)
        self.enemies.add(traffic_car)

    def spawn_random_obstacle(self):
        # Random single obstacle, separate from bigger hazard waves.
        obstacle_class = random.choices(
            [RoadBlock, OilSpill, Pothole],
            weights=[40, 35, 25],
            k=1,
        )[0]
        image = self.barrier_image

        if obstacle_class == OilSpill:
            image = self.oil_image
        elif obstacle_class == Pothole:
            image = self.pothole_image

        y_position = random.randint(-180, -90)
        lane_index = self.find_safe_lane(image, y_position, avoid_player_lane=True)

        if lane_index is None:
            return

        obstacle = obstacle_class(self, lane_index, y_position)

        if isinstance(obstacle, RoadBlock):
            self.add_track_sprite(obstacle, self.lethal_hazards)
        else:
            self.add_track_sprite(obstacle, self.slow_zones)

    def spawn_power_up(self):
        # Only one power-up on the road / active at a time.
        if self.active_power_up or len(self.power_ups) > 0:
            return

        power_up_type = random.choices(
            ["Nitro", "Shield", "Repair"],
            weights=[40, 35, 25],
            k=1,
        )[0]
        image = self.power_up_images[power_up_type]
        y_position = random.randint(-190, -100)
        lane_index = self.find_safe_lane(image, y_position, avoid_player_lane=True)

        if lane_index is None:
            return

        power_up = PowerUp(self, power_up_type, image, lane_index, y_position)
        self.all_sprites.add(power_up)
        self.power_ups.add(power_up)

    def spawn_hazard_wave(self):
        # Wave blocks some lanes but keeps one lane as a safe path.
        safe_lane = random.randrange(self.lane_count)
        y_position = random.randint(-170, -90)

        for lane_index in range(self.lane_count):
            if lane_index == safe_lane:
                continue

            hazard_class = random.choices(
                [RoadBlock, OilSpill, SpeedBump, Pothole],
                weights=[40, 25, 18, 17],
                k=1,
            )[0]
            image = self.get_track_object_image(hazard_class)

            if not self.is_spawn_safe(image, lane_index, y_position):
                continue

            hazard = hazard_class(self, lane_index, y_position + random.randint(-12, 12))

            if isinstance(hazard, RoadBlock):
                self.add_track_sprite(hazard, self.lethal_hazards)
            else:
                self.add_track_sprite(hazard, self.slow_zones)

    def get_track_object_image(self, object_class):
        if object_class == OilSpill:
            return self.oil_image
        if object_class == SpeedBump:
            return self.speed_bump_image
        if object_class == NitroStrip:
            return self.nitro_image
        if object_class == Pothole:
            return self.pothole_image
        return self.barrier_image

    def spawn_road_event(self):
        # Extra dynamic road events to make the track less empty.
        event_class = random.choices(
            [MovingBarrier, SpeedBump, NitroStrip],
            weights=[35, 30, 35],
            k=1,
        )[0]
        y_position = random.randint(-150, -70)
        lane_index = self.find_safe_lane(self.get_track_object_image(event_class), y_position)

        if lane_index is None:
            return

        event = event_class(self, lane_index, y_position)

        if isinstance(event, MovingBarrier):
            self.add_track_sprite(event, self.lethal_hazards)
        elif isinstance(event, NitroStrip):
            self.add_track_sprite(event, self.nitro_strips)
        else:
            self.add_track_sprite(event, self.slow_zones)

    def spawn_checkpoint(self):
        self.add_track_sprite(CheckpointLine(self), self.checkpoints)

    def activate_player_speed(self, speed, duration, message):
        # Normal road effects should not cancel active Nitro.
        if self.active_power_up == "Nitro" and speed < self.boosted_player_speed:
            return

        self.player_speed = speed
        self.speed_effect_end_time = pygame.time.get_ticks() + duration
        self.speed_effect_message = message

    def update_player_speed_effect(self):
        if self.speed_effect_end_time and pygame.time.get_ticks() >= self.speed_effect_end_time:
            if self.active_power_up != "Nitro":
                self.player_speed = self.base_player_speed

            self.speed_effect_end_time = 0
            self.speed_effect_message = ""

    def activate_power_up(self, power_up_type):
        # Nitro and Shield are active effects, Repair is instant.
        if power_up_type == "Repair":
            self.clear_nearest_danger()
            self.power_up_bonus += 75
            self.speed_effect_message = "Repair used"
            self.speed_effect_end_time = pygame.time.get_ticks() + 1200
            return

        if self.active_power_up:
            return

        self.active_power_up = power_up_type

        if power_up_type == "Nitro":
            duration = random.randint(3000, 5000)
            self.power_up_bonus += 50
            self.player_speed = self.boosted_player_speed
            self.active_power_up_end_time = pygame.time.get_ticks() + duration
        elif power_up_type == "Shield":
            self.power_up_bonus += 50
            self.shield_charges = 1
            self.active_power_up_end_time = 0

    def update_active_power_up(self):
        if self.active_power_up != "Nitro":
            return

        if pygame.time.get_ticks() >= self.active_power_up_end_time:
            self.clear_active_power_up()

    def clear_active_power_up(self):
        if self.active_power_up == "Nitro":
            self.player_speed = self.base_player_speed

        self.active_power_up = None
        self.active_power_up_end_time = 0
        self.shield_charges = 0

    def get_power_up_time_text(self):
        if self.active_power_up == "Nitro":
            remaining = max(0, self.active_power_up_end_time - pygame.time.get_ticks())
            return f"{remaining / 1000:.1f}s"

        if self.active_power_up == "Shield":
            return "until hit"

        return ""

    def clear_nearest_danger(self):
        # Repair removes the closest bad object in front of the player.
        dangers = list(self.enemies) + list(self.lethal_hazards) + list(self.slow_zones)

        if not dangers:
            return

        dangers_in_front = [
            danger for danger in dangers
            if danger.rect.centery <= self.player.rect.centery
        ]
        candidates = dangers_in_front or dangers
        nearest_danger = min(
            candidates,
            key=lambda danger: abs(danger.rect.centery - self.player.rect.centery),
        )
        nearest_danger.kill()

    def update_event_timers(self):
        # Main spawning scheduler for traffic, obstacles, power-ups and events.
        current_time = pygame.time.get_ticks()
        self.update_difficulty()

        if current_time >= self.next_traffic_time:
            self.spawn_traffic_car()
            self.next_traffic_time = current_time + random.randint(
                self.get_traffic_delay(),
                self.get_traffic_delay() + 450,
            )

        if current_time >= self.next_obstacle_time:
            self.spawn_random_obstacle()
            self.next_obstacle_time = current_time + random.randint(
                self.get_obstacle_delay(),
                self.get_obstacle_delay() + 650,
            )

        if current_time >= self.next_power_up_time:
            self.spawn_power_up()
            self.next_power_up_time = current_time + random.randint(
                self.get_power_up_delay(),
                self.get_power_up_delay() + 1800,
            )

        if current_time >= self.next_hazard_wave_time:
            self.spawn_hazard_wave()
            self.next_hazard_wave_time = current_time + random.randint(
                self.get_obstacle_delay() + 1200,
                self.get_obstacle_delay() + 2500,
            )

        if current_time >= self.next_road_event_time:
            self.spawn_road_event()
            self.next_road_event_time = current_time + random.randint(
                self.get_obstacle_delay() + 900,
                self.get_obstacle_delay() + 2300,
            )

        if current_time >= self.next_checkpoint_time:
            self.spawn_checkpoint()
            self.next_checkpoint_time = current_time + 5200

    def draw(self):
        # Draw order matters: road objects first, player car last.
        self.display.blit(self.background, (0, 0))
        self.ui.draw_lane_guides(
            self.display,
            self.road_left,
            self.lane_width,
            self.lane_count,
            self.screen_height,
        )
        self.ui.draw_hud(
            self.display,
            self.score,
            self.coins,
            self.enemy_speed,
            self.checkpoints_count,
            self.difficulty_level,
            int(self.distance_traveled),
            self.get_remaining_distance(),
            self.speed_effect_message,
            self.active_power_up,
            self.get_power_up_time_text(),
        )

        for group in (
            self.checkpoints,
            self.slow_zones,
            self.nitro_strips,
            self.lethal_hazards,
            self.power_ups,
            self.coins_group,
            self.enemies,
        ):
            for entity in group:
                entity.move()
                self.display.blit(entity.image, entity.rect)

        self.player.move()
        self.display.blit(self.player.image, self.player.rect)

    def handle_coin_collisions(self):
        # Add coin value and respawn that coin somewhere else.
        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)

        for coin in collected_coins:
            self.coins += coin.value
            coin.reset()

        if self.coins - self.last_speed_up_coins >= self.coins_needed_for_speed_up:
            self.enemy_speed_bonus += 1
            self.last_speed_up_coins = self.coins

    def handle_power_up_collisions(self):
        # Collect power-up if rules allow it.
        collected_power_ups = pygame.sprite.spritecollide(self.player, self.power_ups, False)

        for power_up in collected_power_ups:
            if self.active_power_up and power_up.power_up_type != "Repair":
                continue

            self.activate_power_up(power_up.power_up_type)
            power_up.kill()

    def handle_track_effect_collisions(self):
        # Oil, potholes and speed bumps slow player for a short time.
        touched_slow_zones = pygame.sprite.spritecollide(self.player, self.slow_zones, False)

        for zone in touched_slow_zones:
            if not zone.used:
                self.activate_player_speed(zone.effect_speed, zone.effect_duration, zone.effect_name)
                zone.used = True
                zone.kill()

        touched_nitro_strips = pygame.sprite.spritecollide(self.player, self.nitro_strips, False)

        for strip in touched_nitro_strips:
            if not strip.used:
                self.activate_player_speed(strip.effect_speed, strip.effect_duration, strip.effect_name)
                strip.used = True
                strip.kill()

    def handle_checkpoints(self):
        # Count each checkpoint only once.
        for checkpoint in self.checkpoints:
            if not checkpoint.scored and checkpoint.rect.centery >= self.player.rect.centery:
                self.checkpoints_count += 1
                checkpoint.scored = True

    def get_crash_sprite(self):
        return (
            pygame.sprite.spritecollideany(self.player, self.enemies)
            or pygame.sprite.spritecollideany(self.player, self.lethal_hazards)
        )

    def handle_crash(self):
        # Shield saves player from one crash, otherwise run ends.
        crash_sprite = self.get_crash_sprite()

        if not crash_sprite:
            return

        if self.active_power_up == "Shield" and self.shield_charges > 0:
            crash_sprite.kill()
            self.power_up_bonus += 100
            self.clear_active_power_up()
            self.speed_effect_message = "Shield used"
            self.speed_effect_end_time = pygame.time.get_ticks() + 1200
            return

        self.game_over()

    def play_crash_sound(self):
        if not self.mixer_ready or not self.settings["sound_enabled"]:
            return

        pygame.mixer.music.stop()
        pygame.mixer.Sound(os.path.join(RESOURCE_PATH, "crash.wav")).play()

    def save_result(self):
        # Save current run to leaderboard.json.
        self.score = self.calculate_score()
        add_leaderboard_entry(
            self.username,
            self.score,
            int(self.distance_traveled),
            self.coins,
            self.checkpoints_count,
        )

    def end_run(self, title, play_crash_sound=False):
        # Switch to game-over screen instead of closing instantly.
        if not self.result_saved:
            self.save_result()
            self.result_saved = True

        if play_crash_sound:
            self.play_crash_sound()
        elif self.mixer_ready:
            pygame.mixer.music.stop()

        self.last_run_stats = {
            "title": title,
            "score": self.score,
            "distance": int(self.distance_traveled),
            "coins": self.coins,
        }
        self.screen = "game_over"

        for entity in self.all_sprites:
            entity.kill()

    def game_over(self):
        self.end_run("Game Over", play_crash_sound=True)

    def finish_run(self):
        self.end_run("Finish!", play_crash_sound=False)

    def go_to_main_menu(self):
        self.screen = "menu"
        self.buttons = []
        if self.settings["sound_enabled"]:
            self.start_music()

    def start_name_entry(self):
        self.username_input = ""
        self.screen = "name_entry"

    def start_playing(self):
        # After name entry, make a fresh race.
        self.username = self.username_input.strip() or "Player"
        self.reset_run_state()
        self.screen = "playing"
        if self.settings["sound_enabled"]:
            self.start_music()

    def open_leaderboard(self):
        self.screen = "leaderboard"

    def open_settings(self):
        self.screen = "settings"

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_button_action(self, action):
        # All menu/settings buttons arrive here as action strings.
        if action == "play":
            self.start_name_entry()
        elif action == "leaderboard":
            self.open_leaderboard()
        elif action == "settings":
            self.open_settings()
        elif action == "quit":
            self.quit_game()
        elif action == "main_menu":
            self.go_to_main_menu()
        elif action == "retry":
            self.reset_run_state()
            self.screen = "playing"
            if self.settings["sound_enabled"]:
                self.start_music()
        elif action == "toggle_sound":
            self.settings["sound_enabled"] = not self.settings["sound_enabled"]
            self.apply_settings()
        elif action.startswith("car_"):
            self.settings["car_color"] = action.replace("car_", "")
            self.apply_settings()
        elif action.startswith("difficulty_"):
            self.settings["difficulty"] = action.replace("difficulty_", "")
            self.apply_settings()

    def handle_click(self, position):
        # Mouse clicks are checked against the current screen buttons.
        for button in self.buttons:
            if button.rect.collidepoint(position):
                self.handle_button_action(button.action)
                return

    def handle_keydown(self, event):
        # Keyboard is mainly for name entry and Escape navigation.
        if self.screen == "name_entry":
            if event.key == K_RETURN:
                self.start_playing()
            elif event.key == K_BACKSPACE:
                self.username_input = self.username_input[:-1]
            elif event.key == K_ESCAPE:
                self.go_to_main_menu()
            elif event.unicode.isprintable() and len(self.username_input) < 10:
                self.username_input += event.unicode
        elif event.key == K_ESCAPE and self.screen != "playing":
            self.go_to_main_menu()

    def update_playing(self):
        # One frame of actual gameplay.
        self.update_player_speed_effect()
        self.update_active_power_up()
        self.update_distance()
        self.update_event_timers()
        self.draw()
        self.handle_coin_collisions()
        self.handle_power_up_collisions()
        self.handle_track_effect_collisions()
        self.handle_checkpoints()
        self.handle_crash()

        if self.screen == "playing" and self.distance_traveled >= self.race_distance:
            self.finish_run()

    def draw_screen(self):
        # Draw current screen; gameplay screen also updates movement.
        if self.screen == "menu":
            self.buttons = self.ui.draw_main_menu(self.display)
        elif self.screen == "name_entry":
            self.buttons = self.ui.draw_name_entry(self.display, self.username_input)
        elif self.screen == "settings":
            self.buttons = self.ui.draw_settings_screen(
                self.display,
                self.settings,
                list(CAR_COLOR_TINTS.keys()),
                list(DIFFICULTY_MULTIPLIERS.keys()),
            )
        elif self.screen == "leaderboard":
            self.buttons = self.ui.draw_leaderboard_screen(self.display, load_leaderboard())
        elif self.screen == "game_over":
            stats = self.last_run_stats or {
                "title": "Game Over",
                "score": self.score,
                "distance": int(self.distance_traveled),
                "coins": self.coins,
            }
            self.buttons = self.ui.draw_game_over_screen(self.display, stats["title"], stats)
        elif self.screen == "playing":
            self.buttons = []
            self.update_playing()

    def run(self):
        # Main pygame loop. It never exits unless player quits.
        self.screen = "menu"

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    self.handle_keydown(event)
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.draw_screen()
            pygame.display.update()
            self.clock.tick(self.fps)
