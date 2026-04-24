import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (120, 120, 120)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 200, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 180, 180)

# Fonts
font = pygame.font.SysFont("Arial", 22)

# Canvas surface
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Tools
BRUSH = "brush"
RECTANGLE = "rectangle"
CIRCLE = "circle"
ERASER = "eraser"

current_tool = BRUSH
current_color = BLACK
brush_size = 6

# Drawing state
drawing = False
start_pos = None
last_pos = None
current_pos = None

# Tool buttons
tool_buttons = {
    BRUSH: pygame.Rect(20, 20, 100, 40),
    RECTANGLE: pygame.Rect(140, 20, 120, 40),
    CIRCLE: pygame.Rect(280, 20, 100, 40),
    ERASER: pygame.Rect(400, 20, 100, 40),
}

# Color buttons
color_buttons = [
    (BLACK, pygame.Rect(560, 20, 35, 35)),
    (RED, pygame.Rect(605, 20, 35, 35)),
    (GREEN, pygame.Rect(650, 20, 35, 35)),
    (BLUE, pygame.Rect(695, 20, 35, 35)),
    (YELLOW, pygame.Rect(740, 20, 35, 35)),
    (PURPLE, pygame.Rect(785, 20, 35, 35)),
    (CYAN, pygame.Rect(830, 20, 35, 35)),
]


def draw_toolbar():
    """Draw top toolbar with tools and colors."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    for tool, rect in tool_buttons.items():
        color = DARK_GRAY if current_tool == tool else WHITE
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        label = font.render(tool.capitalize(), True, BLACK)
        screen.blit(label, (rect.x + 10, rect.y + 8))

    for color_value, rect in color_buttons:
        pygame.draw.rect(screen, color_value, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        if color_value == current_color:
            pygame.draw.rect(screen, DARK_GRAY, rect, 4)

    info = font.render(f"Size: {brush_size}", True, BLACK)
    screen.blit(info, (900, 28))


def inside_canvas(pos):
    """Check if mouse is inside the drawing area."""
    return CANVAS_RECT.collidepoint(pos)


def to_canvas_pos(pos):
    """Convert screen position to canvas position."""
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)


def draw_preview():
    """Draw temporary preview for rectangle or circle."""
    if not drawing or start_pos is None or current_pos is None:
        return

    if current_tool == RECTANGLE:
        x1, y1 = to_canvas_pos(start_pos)
        x2, y2 = to_canvas_pos(current_pos)
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(screen, current_color, rect.move(0, TOOLBAR_HEIGHT), 2)

    elif current_tool == CIRCLE:
        x1, y1 = to_canvas_pos(start_pos)
        x2, y2 = to_canvas_pos(current_pos)
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(screen, current_color, start_pos, radius, 2)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Small keyboard shortcuts
            if event.key == pygame.K_b:
                current_tool = BRUSH
            elif event.key == pygame.K_r:
                current_tool = RECTANGLE
            elif event.key == pygame.K_c:
                current_tool = CIRCLE
            elif event.key == pygame.K_e:
                current_tool = ERASER

            # Change size
            elif event.key == pygame.K_UP:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_DOWN:
                brush_size = max(1, brush_size - 1)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Select tool
            for tool, rect in tool_buttons.items():
                if rect.collidepoint(mouse_pos):
                    current_tool = tool

            # Select color
            for color_value, rect in color_buttons:
                if rect.collidepoint(mouse_pos):
                    current_color = color_value

            # Start drawing
            if inside_canvas(mouse_pos):
                drawing = True
                start_pos = mouse_pos
                current_pos = mouse_pos
                last_pos = to_canvas_pos(mouse_pos)

                # Draw first point for brush/eraser
                if current_tool == BRUSH:
                    pygame.draw.circle(canvas, current_color, last_pos, brush_size)
                elif current_tool == ERASER:
                    pygame.draw.circle(canvas, WHITE, last_pos, brush_size)

        if event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                current_pos = event.pos
                canvas_pos = to_canvas_pos(event.pos)

                # Freehand brush
                if current_tool == BRUSH:
                    pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size * 2)
                    pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)

                # Eraser works like white brush
                elif current_tool == ERASER:
                    pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, brush_size * 2)
                    pygame.draw.circle(canvas, WHITE, canvas_pos, brush_size)

                last_pos = canvas_pos

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and start_pos is not None and current_pos is not None:
                end_pos = event.pos

                # Final rectangle
                if current_tool == RECTANGLE and inside_canvas(end_pos):
                    x1, y1 = to_canvas_pos(start_pos)
                    x2, y2 = to_canvas_pos(end_pos)
                    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(canvas, current_color, rect, 2)

                # Final circle
                elif current_tool == CIRCLE and inside_canvas(end_pos):
                    x1, y1 = to_canvas_pos(start_pos)
                    x2, y2 = to_canvas_pos(end_pos)
                    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                    pygame.draw.circle(canvas, current_color, (x1, y1), radius, 2)

            drawing = False
            start_pos = None
            current_pos = None
            last_pos = None

    # Draw UI
    screen.fill(WHITE)
    draw_toolbar()

    # Draw canvas
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, BLACK, CANVAS_RECT, 2)

    # Draw temporary shape preview
    draw_preview()

    pygame.display.flip()
    clock.tick(60)