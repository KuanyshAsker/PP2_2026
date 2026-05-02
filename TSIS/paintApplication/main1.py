import pygame
import sys
import math
import os
from datetime import datetime

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 1100, 700
TOOLBAR_HEIGHT = 145
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# UI colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (232, 235, 240)
PANEL = (247, 248, 251)
PANEL_DARK = (224, 228, 235)
DARK_GRAY = (95, 95, 95)
BORDER = (70, 76, 86)
HOVER = (238, 243, 255)
ACTIVE = (190, 214, 255)
BUTTON = (255, 255, 255)
BLUE_ACCENT = (70, 130, 255)
SOFT_SHADOW = (205, 210, 218)
CANVAS_BG = (245, 246, 248)

# Paint colors
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 200, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 180, 180)
ORANGE = (255, 120, 0)

# Fonts
font = pygame.font.SysFont("Arial", 16)
button_font = pygame.font.SysFont("Arial", 15)
small_font = pygame.font.SysFont("Arial", 12)
title_font = pygame.font.SysFont("Arial", 13, bold=True)
status_font = pygame.font.SysFont("Arial", 14)

# Canvas surface where drawings are saved
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Tool names
BRUSH = "brush"
PENCIL = "pencil"
LINE = "line"
FILL = "fill"
TEXT = "text"
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
    (PENCIL, "Pencil", "P"),
    (LINE, "Line", "L"),
    (FILL, "Fill", "F"),
    (TEXT, "Text", "X"),
    (RECTANGLE, "Rect", "R"),
    (CIRCLE, "Circle", "C"),
    (ERASER, "Eraser", "E"),
    (SQUARE, "Square", "S"),
    (RIGHT_TRIANGLE, "R-Tri", "T"),
    (EQUILATERAL_TRIANGLE, "E-Tri", "Q"),
    (RHOMBUS, "Rhomb", "H"),
]

# Brush/stroke size levels
SMALL_SIZE = 2
MEDIUM_SIZE = 5
LARGE_SIZE = 10

# Font sizes are linked to the same S/M/L size buttons.
TEXT_FONT_SIZES = {
    SMALL_SIZE: 18,
    MEDIUM_SIZE: 28,
    LARGE_SIZE: 42,
}

# Current selected options
current_tool = BRUSH
current_color = BLACK
brush_size = MEDIUM_SIZE
status_message = "Ready"
status_time = 0

# Drawing state variables
drawing = False
start_pos = None
last_pos = None
current_pos = None

# Text tool state
typing_text = False
text_pos = None
text_content = ""

# Undo history
undo_stack = []
MAX_UNDO = 25


def set_status(message):
    """Show a short helpful message in the toolbar."""
    global status_message, status_time
    status_message = message
    status_time = pygame.time.get_ticks()


def make_tool_buttons():
    """Create compact tool buttons in one clean row."""
    buttons = {}
    x = 18
    y = 34
    gap = 7
    row_gap = 8
    button_height = 30
    max_row_width = WIDTH - 245

    for tool, label, shortcut in TOOL_LABELS:
        button_width = max(52, button_font.size(label)[0] + 16)

        if x + button_width > max_row_width:
            x = 18
            y += button_height + row_gap

        buttons[tool] = pygame.Rect(x, y, button_width, button_height)
        x += button_width + gap

    return buttons


# Toolbar buttons
tool_buttons = make_tool_buttons()

# Color buttons
paint_colors = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
color_buttons = []

for i, color in enumerate(paint_colors):
    color_buttons.append((color, pygame.Rect(18 + i * 34, 111, 24, 24)))

# Current color preview
current_color_rect = pygame.Rect(305, 111, 48, 24)

# Stroke size controls: small, medium, large
size_buttons = [
    ("S", SMALL_SIZE, pygame.Rect(390, 112, 34, 23)),
    ("M", MEDIUM_SIZE, pygame.Rect(431, 112, 34, 23)),
    ("L", LARGE_SIZE, pygame.Rect(472, 112, 34, 23)),
]

# Action buttons
action_button_y = 28
undo_button = pygame.Rect(WIDTH - 206, action_button_y, 84, 30)
clear_button = pygame.Rect(WIDTH - 112, action_button_y, 94, 30)
save_button = pygame.Rect(WIDTH - 206, action_button_y + 38, 84, 30)


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
        set_status("Undo applied")
    else:
        set_status("Nothing to undo")


def save_canvas():
    """Save the current canvas as a PNG file with a timestamp."""
    os.makedirs("assets", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"assets/paint_{timestamp}.png"

    pygame.image.save(canvas, filename)
    print(f"Canvas saved as {filename}")
    set_status(f"Saved: {filename}")

    return filename


def draw_text_center(text, rect, text_color=BLACK, text_font=font):
    """Draw text centered inside a rectangle."""
    label = text_font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_button(rect, label, active=False, disabled=False):
    """Draw a modern compact button."""
    mouse_pos = pygame.mouse.get_pos()

    if disabled:
        fill_color = (220, 223, 229)
        text_color = (145, 145, 145)
        border_color = (160, 164, 172)
    elif active:
        fill_color = ACTIVE
        text_color = BLACK
        border_color = BLUE_ACCENT
    elif rect.collidepoint(mouse_pos):
        fill_color = HOVER
        text_color = BLACK
        border_color = BLUE_ACCENT
    else:
        fill_color = BUTTON
        text_color = BLACK
        border_color = BORDER

    shadow_rect = rect.copy()
    shadow_rect.move_ip(2, 2)
    pygame.draw.rect(screen, SOFT_SHADOW, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, fill_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    draw_text_center(label, rect, text_color, button_font)


def draw_section_label(text, pos):
    """Draw a small section label."""
    label = title_font.render(text, True, DARK_GRAY)
    screen.blit(label, pos)


def draw_toolbar():
    """Draw a cleaner, grouped toolbar."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, PANEL, (8, 8, WIDTH - 16, TOOLBAR_HEIGHT - 16), border_radius=14)
    pygame.draw.rect(screen, PANEL_DARK, (8, 8, WIDTH - 16, TOOLBAR_HEIGHT - 16), 2, border_radius=14)
    pygame.draw.line(screen, BORDER, (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    # Tools section
    draw_section_label("Tools", (18, 11))

    for tool, label, shortcut in TOOL_LABELS:
        rect = tool_buttons[tool]
        draw_button(rect, label, active=(current_tool == tool))

    # Action buttons on the right side
    draw_section_label("Actions", (WIDTH - 206, 11))
    draw_button(undo_button, "Undo", disabled=(len(undo_stack) == 0))
    draw_button(clear_button, "Clear")
    draw_button(save_button, "Save")

    # Colors section
    draw_section_label("Colors", (18, 92))

    for color_value, rect in color_buttons:
        pygame.draw.circle(screen, color_value, rect.center, 12)
        pygame.draw.circle(screen, BORDER, rect.center, 13, 2)

        # Highlight selected color with a blue ring
        if color_value == current_color:
            pygame.draw.circle(screen, BLUE_ACCENT, rect.center, 17, 3)

    # Current color preview
    draw_section_label("Current", (305, 92))
    pygame.draw.rect(screen, current_color, current_color_rect, border_radius=6)
    pygame.draw.rect(screen, BORDER, current_color_rect, 2, border_radius=6)

    # Stroke size section
    draw_section_label("Size", (390, 92))

    for label, size, rect in size_buttons:
        draw_button(rect, label, active=(brush_size == size))

    # Helpful hints and status
    hint = small_font.render(
        "Shortcuts: B/P/L/F/X/R/C/E/S/T/Q/H  •  1/2/3 size  •  Ctrl/Cmd+Z undo  •  Ctrl/Cmd+S save",
        True,
        DARK_GRAY,
    )
    screen.blit(hint, (535, 102))

    message = status_message
    if pygame.time.get_ticks() - status_time > 3500:
        message = "Ready"

    status = status_font.render(message, True, DARK_GRAY)
    screen.blit(status, (535, 122))


def inside_canvas(pos):
    """Check if the mouse position is inside the drawing canvas."""
    return CANVAS_RECT.collidepoint(pos)


def to_canvas_pos(pos):
    """Convert screen coordinates to canvas coordinates."""
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)


def flood_fill(surface, start_pos, fill_color):
    """
    Fill a closed area using exact color matching.

    This uses pygame.Surface.get_at() and pygame.Surface.set_at(),
    as required for Task 3.3.
    """
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return False

    target_color = surface.get_at((x, y))
    replacement_color = pygame.Color(fill_color[0], fill_color[1], fill_color[2])

    # If the clicked area is already the selected color, nothing changes.
    if target_color == replacement_color:
        return False

    stack = [(x, y)]

    while stack:
        px, py = stack.pop()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue

        # Stop when the pixel color is different from the clicked area color.
        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), replacement_color)

        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))

    return True


def draw_smooth_stroke(surface, color, start, end, width):
    """
    Draw a continuous freehand stroke between two mouse positions.

    This function uses pygame.draw.line() for the main segment, then fills
    the segment with overlapping circles. The circles are very close together,
    so the stroke does not get gaps when the mouse moves fast or curves sharply.
    """
    radius = max(1, width // 2)

    x1, y1 = start
    x2, y2 = end
    distance = math.hypot(x2 - x1, y2 - y1)

    if distance == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    # Main line keeps the stroke connected and satisfies the pencil requirement.
    pygame.draw.line(surface, color, start, end, width)

    # Extra overlap removes gaps caused by square line caps and fast mouse movement.
    spacing = max(1, radius // 2)
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
    if tool == LINE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        pygame.draw.line(
            surface,
            current_color,
            (x1, y1 + offset_y),
            (x2, y2 + offset_y),
            brush_size
        )

    elif tool == RECTANGLE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        rect = pygame.Rect(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1),
        )

        rect.y += offset_y
        pygame.draw.rect(surface, current_color, rect, brush_size)

    elif tool == CIRCLE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        radius = int(math.hypot(x2 - x1, y2 - y1))
        center = (x1, y1 + offset_y)

        pygame.draw.circle(surface, current_color, center, radius, brush_size)

    elif tool == SQUARE:
        rect = get_square_rect(start, end)
        rect.y += offset_y
        pygame.draw.rect(surface, current_color, rect, brush_size)

    elif tool == RIGHT_TRIANGLE:
        points = get_right_triangle_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, brush_size)

    elif tool == EQUILATERAL_TRIANGLE:
        points = get_equilateral_triangle_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, brush_size)

    elif tool == RHOMBUS:
        points = get_rhombus_points(start, end)
        points = [(int(x), int(y + offset_y)) for x, y in points]
        pygame.draw.polygon(surface, current_color, points, brush_size)


def draw_preview():
    """Draw a temporary shape preview while dragging."""
    if not drawing or start_pos is None or current_pos is None:
        return

    shape_tools = [
        LINE,
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


def get_text_font():
    """Return the current text font based on the selected size level."""
    font_size = TEXT_FONT_SIZES.get(brush_size, 28)
    return pygame.font.SysFont("Arial", font_size)


def draw_text_preview():
    """Show the currently typed text before it is confirmed."""
    if not typing_text or text_pos is None:
        return

    text_font = get_text_font()

    x, y = text_pos
    screen_x = x
    screen_y = y + TOOLBAR_HEIGHT

    text_surface = text_font.render(text_content, True, current_color)
    screen.blit(text_surface, (screen_x, screen_y))

    # Blinking text cursor
    current_time = pygame.time.get_ticks()
    if (current_time // 500) % 2 == 0:
        cursor_x = screen_x + text_surface.get_width() + 2
        cursor_top = screen_y
        cursor_bottom = screen_y + text_font.get_height()
        pygame.draw.line(screen, current_color, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)


def confirm_text():
    """Render typed text permanently onto the canvas."""
    global typing_text, text_pos, text_content

    if text_pos is not None and text_content != "":
        save_undo()
        text_font = get_text_font()
        text_surface = text_font.render(text_content, True, current_color)
        canvas.blit(text_surface, text_pos)
        set_status("Text added")

    typing_text = False
    text_pos = None
    text_content = ""


def cancel_text():
    """Cancel text placement without changing the canvas."""
    global typing_text, text_pos, text_content

    typing_text = False
    text_pos = None
    text_content = ""
    set_status("Text cancelled")


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
            set_status(f"Selected {tool}")
            return True

    # Color selection
    for color_value, rect in color_buttons:
        if rect.collidepoint(mouse_pos):
            current_color = color_value
            set_status("Color changed")
            return True

    # Stroke size selection
    for label, size, rect in size_buttons:
        if rect.collidepoint(mouse_pos):
            brush_size = size
            set_status(f"Size: {label}")
            return True

    # Undo button
    if undo_button.collidepoint(mouse_pos):
        undo()
        return True

    # Clear button
    if clear_button.collidepoint(mouse_pos):
        save_undo()
        canvas.fill(WHITE)
        set_status("Canvas cleared")
        return True

    # Save button
    if save_button.collidepoint(mouse_pos):
        save_canvas()
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

            # Text tool input comes first so letters are typed onto the canvas.
            if typing_text:
                if event.key == pygame.K_RETURN:
                    confirm_text()
                elif event.key == pygame.K_ESCAPE:
                    cancel_text()
                elif event.key == pygame.K_BACKSPACE:
                    text_content = text_content[:-1]
                elif event.unicode:
                    text_content += event.unicode

                continue

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Undo with Ctrl+Z or Cmd+Z
            elif event.key == pygame.K_z and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                undo()

            # Save canvas with Ctrl+S or Cmd+S
            elif event.key == pygame.K_s and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                save_canvas()

            # Stroke size shortcuts
            elif event.key == pygame.K_1:
                brush_size = SMALL_SIZE
                set_status("Size: Small")
            elif event.key == pygame.K_2:
                brush_size = MEDIUM_SIZE
                set_status("Size: Medium")
            elif event.key == pygame.K_3:
                brush_size = LARGE_SIZE
                set_status("Size: Large")

            # Keyboard shortcuts for tools
            elif event.key == pygame.K_p:
                current_tool = PENCIL
                set_status("Selected pencil")
            elif event.key == pygame.K_l:
                current_tool = LINE
                set_status("Selected line")
            elif event.key == pygame.K_f:
                current_tool = FILL
                set_status("Selected fill")
            elif event.key == pygame.K_x:
                current_tool = TEXT
                set_status("Selected text")
            elif event.key == pygame.K_b:
                current_tool = BRUSH
                set_status("Selected brush")
            elif event.key == pygame.K_r:
                current_tool = RECTANGLE
                set_status("Selected rectangle")
            elif event.key == pygame.K_c:
                current_tool = CIRCLE
                set_status("Selected circle")
            elif event.key == pygame.K_e:
                current_tool = ERASER
                set_status("Selected eraser")
            elif event.key == pygame.K_s:
                current_tool = SQUARE
                set_status("Selected square")
            elif event.key == pygame.K_t:
                current_tool = RIGHT_TRIANGLE
                set_status("Selected right triangle")
            elif event.key == pygame.K_q:
                current_tool = EQUILATERAL_TRIANGLE
                set_status("Selected equilateral triangle")
            elif event.key == pygame.K_h:
                current_tool = RHOMBUS
                set_status("Selected rhombus")

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # If the click was on toolbar, do not start drawing
            if handle_toolbar_click(mouse_pos):
                continue

            # Start drawing only inside the canvas
            if inside_canvas(mouse_pos):
                if current_tool == TEXT:
                    typing_text = True
                    text_pos = to_canvas_pos(mouse_pos)
                    text_content = ""
                    set_status("Typing text: Enter confirms, Escape cancels")
                    continue

                if current_tool == FILL:
                    canvas_pos = to_canvas_pos(mouse_pos)

                    # Save undo only if the fill will actually change pixels.
                    if canvas.get_at(canvas_pos) != pygame.Color(current_color[0], current_color[1], current_color[2]):
                        save_undo()
                        flood_fill(canvas, canvas_pos, current_color)
                        set_status("Area filled")
                    else:
                        set_status("Area already has this color")

                    continue

                drawing = True
                start_pos = mouse_pos
                current_pos = mouse_pos
                last_pos = to_canvas_pos(mouse_pos)

                # Save undo before freehand drawing starts
                if current_tool in [BRUSH, PENCIL, ERASER]:
                    save_undo()

                # Draw first point for brush, pencil, or eraser
                if current_tool == BRUSH:
                    draw_smooth_stroke(canvas, current_color, last_pos, last_pos, brush_size)

                elif current_tool == PENCIL:
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

                # Pencil drawing: continuous pygame.draw.line-based stroke with gap filling.
                elif current_tool == PENCIL:
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
                    LINE,
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

    # Draw app background
    screen.fill(CANVAS_BG)
    draw_toolbar()

    # Draw canvas below toolbar
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, BORDER, CANVAS_RECT, 2)

    # Draw temporary shape preview
    draw_preview()

    # Draw temporary text preview while typing
    draw_text_preview()

    # Update the display
    pygame.display.flip()
    clock.tick(60)
