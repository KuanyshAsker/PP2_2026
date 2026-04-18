import pygame
from ball import Ball

WIDTH = 800
HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")
clock = pygame.time.Clock()

ball = Ball(WIDTH, HEIGHT)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ball.move(-ball.step, 0)
            elif event.key == pygame.K_RIGHT:
                ball.move(ball.step, 0)
            elif event.key == pygame.K_UP:
                ball.move(0, -ball.step)
            elif event.key == pygame.K_DOWN:
                ball.move(0, ball.step)

    screen.fill((255, 255, 255))
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()