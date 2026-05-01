import datetime
import pygame

from tools import (
    draw_pencil,
    draw_line,
    draw_rectangle,
    draw_square,
    draw_circle,
    draw_right_triangle,
    draw_equilateral_triangle,
    draw_rhombus,
    flood_fill
)


class PaintApp:
    def __init__(self):
        pygame.init()

        self.width = 1100
        self.height = 750
        self.toolbar_height = 110

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("TSIS2 Paint")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 26)

        self.canvas = pygame.Surface((self.width, self.height - self.toolbar_height))
        self.canvas.fill((255, 255, 255))

        self.running = True
        self.drawing = False

        self.current_tool = "pencil"
        self.current_color = (0, 0, 0)
        self.brush_size = 5

        self.start_pos = None
        self.last_pos = None
        self.preview_canvas = None

        self.text_mode = False
        self.text_position = None
        self.text_buffer = ""

        self.colors = {
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 180, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 220, 0),
            "white": (255, 255, 255)
        }

    def get_canvas_pos(self, mouse_pos):
        x, y = mouse_pos
        return x, y - self.toolbar_height

    def is_inside_canvas(self, mouse_pos):
        x, y = mouse_pos
        return 0 <= x < self.width and self.toolbar_height <= y < self.height

    def save_canvas(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"paint_{timestamp}.png"
        pygame.image.save(self.canvas, filename)
        print(f"Saved as {filename}")

    def confirm_text(self):
        if self.text_position is None:
            return

        text_surface = self.font.render(self.text_buffer, True, self.current_color)
        self.canvas.blit(text_surface, self.text_position)

        self.text_mode = False
        self.text_position = None
        self.text_buffer = ""

    def cancel_text(self):
        self.text_mode = False
        self.text_position = None
        self.text_buffer = ""

    def handle_keydown(self, event):
        if self.text_mode:
            if event.key == pygame.K_RETURN:
                self.confirm_text()
                return

            if event.key == pygame.K_ESCAPE:
                self.cancel_text()
                return

            if event.key == pygame.K_BACKSPACE:
                self.text_buffer = self.text_buffer[:-1]
                return

            if event.unicode:
                self.text_buffer += event.unicode
                return

        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_p:
            self.current_tool = "pencil"

        elif event.key == pygame.K_l:
            self.current_tool = "line"

        elif event.key == pygame.K_r:
            self.current_tool = "rectangle"

        elif event.key == pygame.K_s and not (event.mod & pygame.KMOD_CTRL):
            self.current_tool = "square"

        elif event.key == pygame.K_c:
            self.current_tool = "circle"

        elif event.key == pygame.K_h:
            self.current_tool = "right_triangle"

        elif event.key == pygame.K_j:
            self.current_tool = "equilateral_triangle"

        elif event.key == pygame.K_k:
            self.current_tool = "rhombus"

        elif event.key == pygame.K_e:
            self.current_tool = "eraser"

        elif event.key == pygame.K_f:
            self.current_tool = "fill"

        elif event.key == pygame.K_t:
            self.current_tool = "text"

        elif event.key == pygame.K_1:
            self.brush_size = 2

        elif event.key == pygame.K_2:
            self.brush_size = 5

        elif event.key == pygame.K_3:
            self.brush_size = 10

        elif event.key == pygame.K_b:
            self.current_color = self.colors["black"]

        elif event.key == pygame.K_q:
            self.current_color = self.colors["red"]

        elif event.key == pygame.K_w:
            self.current_color = self.colors["green"]

        elif event.key == pygame.K_a:
            self.current_color = self.colors["blue"]

        elif event.key == pygame.K_y:
            self.current_color = self.colors["yellow"]

        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
            self.save_canvas()

    def handle_mouse_down(self, event):
        if not self.is_inside_canvas(event.pos):
            return

        canvas_pos = self.get_canvas_pos(event.pos)

        if self.current_tool == "fill":
            flood_fill(self.canvas, canvas_pos, self.current_color)
            return

        if self.current_tool == "text":
            self.text_mode = True
            self.text_position = canvas_pos
            self.text_buffer = ""
            return

        self.drawing = True
        self.start_pos = canvas_pos
        self.last_pos = canvas_pos
        self.preview_canvas = self.canvas.copy()

    def handle_mouse_motion(self, event):
        if not self.drawing:
            return

        if not self.is_inside_canvas(event.pos):
            return

        canvas_pos = self.get_canvas_pos(event.pos)

        if self.current_tool == "pencil":
            draw_pencil(
                self.canvas,
                self.current_color,
                self.last_pos,
                canvas_pos,
                self.brush_size
            )
            self.last_pos = canvas_pos

        elif self.current_tool == "eraser":
            draw_pencil(
                self.canvas,
                (255, 255, 255),
                self.last_pos,
                canvas_pos,
                self.brush_size
            )
            self.last_pos = canvas_pos

    def handle_mouse_up(self, event):
        if not self.drawing:
            return

        if not self.is_inside_canvas(event.pos):
            self.drawing = False
            return

        end_pos = self.get_canvas_pos(event.pos)
        self.draw_final_shape(self.canvas, self.start_pos, end_pos)

        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_canvas = None

    def draw_final_shape(self, surface, start_pos, end_pos):
        if self.current_tool == "line":
            draw_line(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "rectangle":
            draw_rectangle(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "square":
            draw_square(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "circle":
            draw_circle(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "right_triangle":
            draw_right_triangle(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "equilateral_triangle":
            draw_equilateral_triangle(surface, self.current_color, start_pos, end_pos, self.brush_size)

        elif self.current_tool == "rhombus":
            draw_rhombus(surface, self.current_color, start_pos, end_pos, self.brush_size)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

    def draw_toolbar(self):
        toolbar_rect = pygame.Rect(0, 0, self.width, self.toolbar_height)
        pygame.draw.rect(self.screen, (220, 220, 220), toolbar_rect)

        title = self.big_font.render("TSIS2 Paint", True, (0, 0, 0))
        self.screen.blit(title, (15, 10))

        tool_text = (
            f"Tool: {self.current_tool} | "
            f"Size: {self.brush_size} | "
            f"Color: {self.current_color}"
        )
        surface = self.font.render(tool_text, True, (0, 0, 0))
        self.screen.blit(surface, (15, 45))

        help_1 = (
            "P pencil | L line | R rect | S square | C circle | "
            "H right triangle | J triangle | K rhombus"
        )
        help_2 = (
            "E eraser | F fill | T text | 1/2/3 size | "
            "B black Q red W green A blue Y yellow | Ctrl+S save"
        )

        self.screen.blit(self.font.render(help_1, True, (0, 0, 0)), (15, 70))
        self.screen.blit(self.font.render(help_2, True, (0, 0, 0)), (15, 90))

    def draw_preview(self):
        if not self.drawing:
            return

        if self.current_tool not in [
            "line",
            "rectangle",
            "square",
            "circle",
            "right_triangle",
            "equilateral_triangle",
            "rhombus"
        ]:
            return

        mouse_pos = pygame.mouse.get_pos()

        if not self.is_inside_canvas(mouse_pos):
            return

        end_pos = self.get_canvas_pos(mouse_pos)
        preview = self.preview_canvas.copy()

        self.draw_final_shape(preview, self.start_pos, end_pos)
        self.screen.blit(preview, (0, self.toolbar_height))

    def draw_text_preview(self):
        if not self.text_mode or self.text_position is None:
            return

        text_surface = self.font.render(self.text_buffer + "|", True, self.current_color)
        x, y = self.text_position
        self.screen.blit(text_surface, (x, y + self.toolbar_height))

    def draw(self):
        self.screen.fill((255, 255, 255))

        self.draw_toolbar()
        self.screen.blit(self.canvas, (0, self.toolbar_height))

        self.draw_preview()
        self.draw_text_preview()

        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    app = PaintApp()
    app.run()


if __name__ == "__main__":
    main()