import pygame


def draw_pencil(surface, color, start_pos, end_pos, size):
    pygame.draw.line(surface, color, start_pos, end_pos, size)


def draw_line(surface, color, start_pos, end_pos, size):
    pygame.draw.line(surface, color, start_pos, end_pos, size)


def draw_rectangle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, rect, size)


def draw_circle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

    if radius > 0:
        pygame.draw.circle(surface, color, start_pos, radius, size)


def flood_fill(surface, start_pos, fill_color):
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    target_color = surface.get_at((x, y))

    if target_color == fill_color:
        return

    stack = [(x, y)]

    while stack:
        current_x, current_y = stack.pop()

        if current_x < 0 or current_x >= width:
            continue

        if current_y < 0 or current_y >= height:
            continue

        if surface.get_at((current_x, current_y)) != target_color:
            continue

        surface.set_at((current_x, current_y), fill_color)

        stack.append((current_x + 1, current_y))
        stack.append((current_x - 1, current_y))
        stack.append((current_x, current_y + 1))
        stack.append((current_x, current_y - 1))