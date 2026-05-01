import pygame

from tools import (
    draw_pencil,
    draw_line,
    draw_rectangle,
    draw_circle,
    flood_fill
)


class PaintApp:
    def __init__(self):
        pygame.init()

        self.width = 1000
        self.height = 700
        self.toolbar_height = 90

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

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False

        if event.key == pygame.K_p:
            self.current_tool = "pencil"

        elif event.key == pygame.K_l:
            self.current_tool = "line"

        elif event.key == pygame.K_r:
            self.current_tool = "rectangle"

        elif event.key == pygame.K_c:
            self.current_tool = "circle"

        elif event.key == pygame.K_e:
            self.current_tool = "eraser"

        elif event.key == pygame.K_f:
            self.current_tool = "fill"

        elif event.key == pygame.K_t:
            self.current_tool = "text"
            self.text_mode = True
            self.text_buffer = ""

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

        elif event.key == pygame.K_BACKSPACE and self.text_mode:
            self.text_buffer = self.text_buffer[:-1]

        elif event.key == pygame.K_RETURN and self.text_mode:
            self.text_mode = False

        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
            pygame.image.save(self.canvas, "paint_output.png")
            print("Saved as paint_output.png")

        elif self.text_mode:
            if event.unicode:
                self.text_buffer += event.unicode

    def handle_mouse_down(self, event):
        if not self.is_inside_canvas(event.pos):
            return

        canvas_pos = self.get_canvas_pos(event.pos)

        if self.current_tool == "fill":
            flood_fill(self.canvas, canvas_pos, self.current_color)
            return

        if self.current_tool == "text":
            text_surface = self.font.render(self.text_buffer, True, self.current_color)
            self.canvas.blit(text_surface, canvas_pos)
            self.text_buffer = ""
            self.text_mode = True
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

        if self.current_tool == "line":
            draw_line(
                self.canvas,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        elif self.current_tool == "rectangle":
            draw_rectangle(
                self.canvas,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        elif self.current_tool == "circle":
            draw_circle(
                self.canvas,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_canvas = None

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

        help_text = (
            "P pencil | L line | R rect | C circle | E eraser | F fill | "
            "T text | 1/2/3 size | B black Q red W green A blue Y yellow | Ctrl+S save"
        )
        help_surface = self.font.render(help_text, True, (0, 0, 0))
        self.screen.blit(help_surface, (15, 68))

    def draw_preview(self):
        if not self.drawing:
            return

        if self.current_tool not in ["line", "rectangle", "circle"]:
            return

        mouse_pos = pygame.mouse.get_pos()

        if not self.is_inside_canvas(mouse_pos):
            return

        end_pos = self.get_canvas_pos(mouse_pos)

        preview = self.preview_canvas.copy()

        if self.current_tool == "line":
            draw_line(
                preview,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        elif self.current_tool == "rectangle":
            draw_rectangle(
                preview,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        elif self.current_tool == "circle":
            draw_circle(
                preview,
                self.current_color,
                self.start_pos,
                end_pos,
                self.brush_size
            )

        self.screen.blit(preview, (0, self.toolbar_height))

    def draw_text_preview(self):
        if not self.text_mode:
            return

        surface = self.font.render(f"Text: {self.text_buffer}", True, (0, 0, 0))
        self.screen.blit(surface, (600, 10))

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