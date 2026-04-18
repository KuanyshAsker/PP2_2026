import pygame
from clock import ImageClock

WIDTH = 800
HEIGHT = 800

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Image Clock")
timer = pygame.time.Clock()

app = ImageClock(WIDTH, HEIGHT)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    app.draw(screen)
    pygame.display.flip()
    timer.tick(30)

pygame.quit()