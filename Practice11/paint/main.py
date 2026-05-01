import pygame
import sys
import math

#Initialize pygame
pygame.init()

#Window settings
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 100
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

#UI colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (225, 227, 232)
DARK_GRAY = (95, 95, 95)
BORDER = (55, 55, 55)
HOVER = (238, 242, 250)
ACTIVE = (180, 205, 255)
BUTTON = (250, 250, 252)
BLUE_ACCENT = (60, 120, 255)

#Paint colors
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 200, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 180, 180)
ORANGE = (255, 120, 0)

#Fonts
font = pygame.font.SysFont("Arial", 16)
button_font = pygame.font.SysFont("Arial", 16)
small_font = pygame.font.SysFont("Arial", 12)
title_font = pygame.font.SysFont("Arial", 13, bold=True)

# Canvas surface where drawings are saved
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Tool names
BRUSH = "brush"
RECTANGLE = "rectangle"
CIRCLE = "circle"
ERASER = "eraser"
SQUARE = "square"
RIGHT_TRIANGLE = "right triangle"
EQUILATERAL_TRIANGLE = "equilateral triangle"
RHOMBUS = "rhombus"

# Short labels keep the toolbar compact and readable
TOOL_LABELS = [
    (BRUSH, "Brush", "B"),
    (RECTANGLE, "Rect", "R"),
    (CIRCLE, "Circle", "C"),
    (ERASER, "Eraser", "E"),
    (SQUARE, "Square", "S"),
    (RIGHT_TRIANGLE, "Right Tri", "T"),
    (EQUILATERAL_TRIANGLE, "Equal Tri", "Q"),
    (RHOMBUS, "Rhombus", "H"),
]

# Current selected options
current_tool = BRUSH
current_color = BLACK
brush_size = 6

# Drawing state variables
drawing = False
start_pos = None
last_pos = None
current_pos = None

# Undo history
undo_stack = []
MAX_UNDO = 25


def make_tool_buttons():
    """Create compact tool buttons in one row."""
    buttons = {}
    x = 14
    y = 22
    gap = 8
    button_height = 30

    for tool, label, shortcut in TOOL_LABELS:
        button_width = max(64, button_font.size(label)[0] + 22)
        buttons[tool] = pygame.Rect(x, y, button_width, button_height)
        x += button_width + gap

    return buttons


# Toolbar buttons
tool_buttons = make_tool_buttons()

# Color buttons
paint_colors = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
color_buttons = []

for i, color in enumerate(paint_colors):
    color_buttons.append((color, pygame.Rect(16 + i * 34, 66, 24, 24)))

# Current color preview
current_color_rect = pygame.Rect(325, 67, 48, 22)

# Brush size controls
minus_button = pygame.Rect(430, 67, 28, 22)
size_box = pygame.Rect(465, 67, 42, 22)
plus_button = pygame.Rect(514, 67, 28, 22)

# Action buttons
undo_button = pygame.Rect(WIDTH - 178, 22, 75, 30)
clear_button = pygame.Rect(WIDTH - 92, 22, 75, 30)


def save_undo():
    """Save a copy of the canvas before changing it."""
    undo_stack.append(canvas.copy())

    # Keep the undo history from growing forever
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)


def undo():
    """Restore the previous canvas state."""
    if undo_stack:
        previous_canvas = undo_stack.pop()
        canvas.blit(previous_canvas, (0, 0))


def draw_text_center(text, rect, text_color=BLACK, text_font=font):
    """Draw text centered inside a rectangle."""
    label = text_font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_button(rect, label, active=False, disabled=False):
    """Draw a clean compact button."""
    mouse_pos = pygame.mouse.get_pos()

    if disabled:
        fill_color = (215, 215, 215)
        text_color = (130, 130, 130)
    elif active:
        fill_color = ACTIVE
        text_color = BLACK
    elif rect.collidepoint(mouse_pos):
        fill_color = HOVER
        text_color = BLACK
    else:
        fill_color = BUTTON
        text_color = BLACK

    pygame.draw.rect(screen, fill_color, rect, border_radius=7)
    pygame.draw.rect(screen, BORDER, rect, 2, border_radius=7)
    draw_text_center(label, rect, text_color, button_font)


def draw_toolbar():
    """Draw a compact toolbar with clean spacing."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, BORDER, (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    # Tools section
    tools_label = title_font.render("Tools", True, DARK_GRAY)
    screen.blit(tools_label, (14, 5))

    for tool, label, shortcut in TOOL_LABELS:
        rect = tool_buttons[tool]
        draw_button(rect, label, active=(current_tool == tool))

    # Undo and Clear buttons are on the right side
    draw_button(undo_button, "Undo", disabled=(len(undo_stack) == 0))
    draw_button(clear_button, "Clear")

    # Colors section
    colors_label = title_font.render("Colors", True, DARK_GRAY)
    screen.blit(colors_label, (16, 54))

    for color_value, rect in color_buttons:
        pygame.draw.circle(screen, color_value, rect.center, 12)
        pygame.draw.circle(screen, BORDER, rect.center, 13, 2)

        # Highlight selected color with a blue ring
        if color_value == current_color:
            pygame.draw.circle(screen, BLUE_ACCENT, rect.center, 16, 3)

    # Current color preview
    current_label = title_font.render("Current", True, DARK_GRAY)
    screen.blit(current_label, (325, 54))

    pygame.draw.rect(screen, current_color, current_color_rect, border_radius=5)
    pygame.draw.rect(screen, BORDER, current_color_rect, 2, border_radius=5)

    # Brush size section
    size_label = title_font.render("Brush", True, DARK_GRAY)
    screen.blit(size_label, (430, 54))

    draw_button(minus_button, "-")

    pygame.draw.rect(screen, WHITE, size_box, border_radius=6)
    pygame.draw.rect(screen, BORDER, size_box, 2, border_radius=6)
    draw_text_center(str(brush_size), size_box, BLACK, button_font)

    draw_button(plus_button, "+")

    # Small hint. It is placed after controls so it does not overlap them.
    hint = small_font.render("Mouse wheel or +/- changes brush size.  Cmd/Ctrl+Z = Undo", True, DARK_GRAY)
    screen.blit(hint, (585, 70))


def inside_canvas(pos):
    """Check if the mouse position is inside the drawing canvas."""
    return CANVAS_RECT.collidepoint(pos)


def to_canvas_pos(pos):
    """Convert screen coordinates to canvas coordinates."""
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)


def draw_smooth_stroke(surface, color, start, end, radius):
    """
    Draw a smooth brush/eraser stroke between two points.

    Instead of drawing a line and then adding separate circles, this function
    places many overlapping circles between the old and new mouse positions.
    That removes the dotted look and creates smoother freehand strokes.
    """
    x1, y1 = start
    x2, y2 = end
    distance = math.hypot(x2 - x1, y2 - y1)

    if distance == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    # Smaller spacing means the circles overlap more, so the stroke looks smoother.
    spacing = max(1, radius // 3)
    steps = max(1, int(distance / spacing))

    for i in range(steps + 1):
        t = i / steps
        x = round(x1 + (x2 - x1) * t)
        y = round(y1 + (y2 - y1) * t)
        pygame.draw.circle(surface, color, (x, y), radius)


def get_square_rect(start, end):
    """Create a square from the starting mouse position to the ending mouse position."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    width = x2 - x1
    height = y2 - y1

    # A square must have equal width and height
    side = min(abs(width), abs(height))

    # Keep the square in the direction the user dragged
    if width < 0:
        x1 -= side
    if height < 0:
        y1 -= side

    return pygame.Rect(x1, y1, side, side)


def get_right_triangle_points(start, end):
    """Return three points for a right triangle."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    # The right angle is created using one vertical and one horizontal side
    return [
        (x1, y1),
        (x1, y2),
        (x2, y2),
    ]


def get_equilateral_triangle_points(start, end):
    """Return three points for an equilateral triangle."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    # The side length is based on horizontal mouse movement
    side = x2 - x1
    triangle_height = abs(side) * math.sqrt(3) / 2

    if side < 0:
        left_x = x2
        right_x = x1
    else:
        left_x = x1
        right_x = x2

    # Dragging down creates a triangle pointing up.
    # Dragging up creates a triangle pointing down.
    if y2 > y1:
        base_y = y2
        top_y = base_y - triangle_height
    else:
        base_y = y2
        top_y = base_y + triangle_height

    top_x = (left_x + right_x) / 2

    return [
        (top_x, top_y),
        (left_x, base_y),
        (right_x, base_y),
    ]


def get_rhombus_points(start, end):
    """Return four points for a rhombus shaped like a diamond."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    return [
        (center_x, y1),
        (x2, center_y),
        (center_x, y2),
        (x1, center_y),
    ]


def draw_shape(surface, tool, start, end, offset_y=0):
    """
    Draw the selected shape.

    offset_y is used for preview drawing because the canvas starts below the toolbar.
    """
    if tool == RECTANGLE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        rect = pygame.Rect(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1),
        )

        rect.y += offset_y
        pygame.draw.rect(surface, current_color, rect, 2)

    elif tool == CIRCLE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        radius = int(math.hypot(x2 - x1, y2 - y1))
        center = (x1, y1 + offset_y)

        pygame.draw.circle(surface, current_color, center, radius, 2)

    elif tool == SQUARE:
        rect = get_square_rect(start, end)
        rect.y += offset_y
        pygame.draw.rect(surface, current_color, rect, 2)

    elif tool == RIGHT_TRIANGLE:
        points = get_right_triangle_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, 2)

    elif tool == EQUILATERAL_TRIANGLE:
        points = get_equilateral_triangle_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, 2)

    elif tool == RHOMBUS:
        points = get_rhombus_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, 2)


def draw_preview():
    """Draw a temporary shape preview while dragging."""
    if not drawing or start_pos is None or current_pos is None:
        return

    shape_tools = [
        RECTANGLE,
        CIRCLE,
        SQUARE,
        RIGHT_TRIANGLE,
        EQUILATERAL_TRIANGLE,
        RHOMBUS,
    ]

    if current_tool in shape_tools:
        # Clip preview so it stays inside the canvas area
        old_clip = screen.get_clip()
        screen.set_clip(CANVAS_RECT)
        draw_shape(screen, current_tool, start_pos, current_pos, TOOLBAR_HEIGHT)
        screen.set_clip(old_clip)


def handle_toolbar_click(mouse_pos):
    """
    Handle clicks on toolbar buttons.

    Returns True if the click was on the toolbar so drawing should not start.
    """
    global current_tool, current_color, brush_size

    # Tool selection
    for tool, rect in tool_buttons.items():
        if rect.collidepoint(mouse_pos):
            current_tool = tool
            return True

    # Color selection
    for color_value, rect in color_buttons:
        if rect.collidepoint(mouse_pos):
            current_color = color_value
            return True

    # Brush size buttons
    if minus_button.collidepoint(mouse_pos):
        brush_size = max(1, brush_size - 1)
        return True

    if plus_button.collidepoint(mouse_pos):
        brush_size = min(50, brush_size + 1)
        return True

    # Undo button
    if undo_button.collidepoint(mouse_pos):
        undo()
        return True

    # Clear button
    if clear_button.collidepoint(mouse_pos):
        save_undo()
        canvas.fill(WHITE)
        return True

    # Any click inside the toolbar should not draw on the canvas
    return mouse_pos[1] < TOOLBAR_HEIGHT


# Main program loop
while True:
    for event in pygame.event.get():

        # Quit program
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Keyboard controls
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Undo with Ctrl+Z or Cmd+Z
            elif event.key == pygame.K_z and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                undo()

            # Keyboard shortcuts for tools
            elif event.key == pygame.K_b:
                current_tool = BRUSH
            elif event.key == pygame.K_r:
                current_tool = RECTANGLE
            elif event.key == pygame.K_c:
                current_tool = CIRCLE
            elif event.key == pygame.K_e:
                current_tool = ERASER
            elif event.key == pygame.K_s:
                current_tool = SQUARE
            elif event.key == pygame.K_t:
                current_tool = RIGHT_TRIANGLE
            elif event.key == pygame.K_q:
                current_tool = EQUILATERAL_TRIANGLE
            elif event.key == pygame.K_h:
                current_tool = RHOMBUS

            # Change brush size
            elif event.key == pygame.K_UP or event.key == pygame.K_EQUALS:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)

        # Mouse wheel changes brush size
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # If the click was on toolbar, do not start drawing
            if handle_toolbar_click(mouse_pos):
                continue

            # Start drawing only inside the canvas
            if inside_canvas(mouse_pos):
                drawing = True
                start_pos = mouse_pos
                current_pos = mouse_pos
                last_pos = to_canvas_pos(mouse_pos)

                # Save undo before freehand drawing starts
                if current_tool in [BRUSH, ERASER]:
                    save_undo()

                # Draw first point for brush or eraser
                if current_tool == BRUSH:
                    draw_smooth_stroke(canvas, current_color, last_pos, last_pos, brush_size)
                elif current_tool == ERASER:
                    draw_smooth_stroke(canvas, WHITE, last_pos, last_pos, brush_size)

        # Mouse movement while drawing
        if event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                current_pos = event.pos
                canvas_pos = to_canvas_pos(event.pos)

                # Smooth freehand brush drawing
                if current_tool == BRUSH:
                    draw_smooth_stroke(canvas, current_color, last_pos, canvas_pos, brush_size)

                # Smooth eraser drawing
                elif current_tool == ERASER:
                    draw_smooth_stroke(canvas, WHITE, last_pos, canvas_pos, brush_size)

                last_pos = canvas_pos

        # Mouse release
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and start_pos is not None and current_pos is not None:
                end_pos = event.pos

                shape_tools = [
                    RECTANGLE,
                    CIRCLE,
                    SQUARE,
                    RIGHT_TRIANGLE,
                    EQUILATERAL_TRIANGLE,
                    RHOMBUS,
                ]

                # Draw final shape on canvas
                if current_tool in shape_tools and inside_canvas(end_pos):
                    save_undo()
                    draw_shape(canvas, current_tool, start_pos, end_pos)

            # Reset drawing state
            drawing = False
            start_pos = None
            current_pos = None
            last_pos = None

    # Draw UI background and toolbar
    screen.fill(WHITE)
    draw_toolbar()

    # Draw canvas below toolbar
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, BORDER, CANVAS_RECT, 2)

    # Draw temporary shape preview
    draw_preview()

    # Update the display
    pygame.display.flip()
    clock.tick(60)
