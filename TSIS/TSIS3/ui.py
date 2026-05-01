import pygame


def draw_text(screen, text, x, y, font, color=(255, 255, 255)):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_centered_text(screen, text, y, font, color=(255, 255, 255)):
    surface = font.render(text, True, color)
    x = screen.get_width() // 2 - surface.get_width() // 2
    screen.blit(surface, (x, y))