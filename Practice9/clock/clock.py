import pygame
import math
from datetime import datetime
from pathlib import Path


class ImageClock:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        base = Path(__file__).resolve().parent / "images"

        # load face image
        face = pygame.image.load(str(base / "clock_face.jpg")).convert()
        face_size = min(width, height) - 60
        self.face = pygame.transform.smoothscale(face, (face_size, face_size))
        self.face_rect = self.face.get_rect(center=(width // 2, height // 2 - 20))

        # load hand image
        try:
            hand = pygame.image.load(str(base / "clock_hand.svg")).convert_alpha()
        except:
            hand = pygame.image.load(str(base / "clock_hand.png")).convert_alpha()

        # same hand image, different sizes
        self.minute_hand = self.scale_hand(hand, int(self.face_rect.width * 0.25))
        self.second_hand = self.scale_hand(hand, int(self.face_rect.width * 0.34))

        self.center = self.face_rect.center
        self.font = pygame.font.SysFont("arial", 38, bold=True)

    def scale_hand(self, image, target_width):
        w, h = image.get_size()
        scale = target_width / w
        new_size = (int(w * scale), int(h * scale))
        return pygame.transform.smoothscale(image, new_size)

    def draw_hand(self, screen, image, value):
        # this hand points left, so pivot is on the right side
        pivot = (int(image.get_width() * 0.95), image.get_height() // 2)

        # left = 180 deg, clock 0 should point up
        base_angle = 180
        target_angle = 90 - value * 6
        angle = target_angle - base_angle

        rect = image.get_rect(
            topleft=(self.center[0] - pivot[0], self.center[1] - pivot[1])
        )

        offset = pygame.math.Vector2(self.center) - rect.center
        rotated_offset = offset.rotate(-angle)
        rotated_center = (
            self.center[0] - rotated_offset.x,
            self.center[1] - rotated_offset.y
        )

        rotated = pygame.transform.rotate(image, angle)
        rotated_rect = rotated.get_rect(center=rotated_center)
        screen.blit(rotated, rotated_rect)

    def draw(self, screen):
        screen.fill((235, 235, 235))
        screen.blit(self.face, self.face_rect)

        now = datetime.now()
        minute = now.minute
        second = now.second

        minute_value = minute + second / 60

        # draw second first, then minute on top
        self.draw_hand(screen, self.second_hand, second)
        self.draw_hand(screen, self.minute_hand, minute_value)

        # cover the middle a bit
        pygame.draw.circle(screen, (40, 40, 40), self.center, 8)

        # digital time at bottom
        text = self.font.render(f"{minute:02d}:{second:02d}", True, (20, 20, 20))
        text_rect = text.get_rect(center=(self.width // 2, self.height - 40))
        screen.blit(text, text_rect)