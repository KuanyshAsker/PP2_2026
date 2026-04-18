import pygame
from pathlib import Path
from player import MusicPlayer

WIDTH = 950
HEIGHT = 560

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")
clock = pygame.time.Clock()

music_folder = Path(__file__).resolve().parent / "music"
player = MusicPlayer(music_folder)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.pause()
            elif event.key == pygame.K_x:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.previous_track()
            elif event.key == pygame.K_q:
                running = False

    player.update()
    player.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.mixer.music.stop()
pygame.quit()