import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = pygame.Rect(180, 500, 40, 60)
enemy = pygame.Rect(random.randint(0, 360), -60, 40, 60)

speed = 5
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5

    enemy.y += speed
    if enemy.y > HEIGHT:
        enemy.y = -60
        enemy.x = random.randint(0, 360)

    if player.colliderect(enemy):
        print("Game Over")
        running = False

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), player)
    pygame.draw.rect(screen, (255, 0, 0), enemy)

    pygame.display.update()
    clock.tick(60)

pygame.quit()