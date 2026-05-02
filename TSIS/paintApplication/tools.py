import pygame
import math
import os
from datetime import datetime

# =========================
# app settings / constants
# =========================

# fits better on ~1147 x 745 display
WIDTH, HEIGHT = 1100, 700
TOOLBAR_HEIGHT = 145
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

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

# paint colors
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 200, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 180, 180)
ORANGE = (255, 120, 0)

# tool names
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

# short labels so toolbar doesn't look messy
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

# required S / M / L sizes
SMALL_SIZE = 2
MEDIUM_SIZE = 5
LARGE_SIZE = 10

# text uses same size buttons, but font needs bigger values than stroke px
TEXT_FONT_SIZES = {
    SMALL_SIZE: 18,
    MEDIUM_SIZE: 28,
    LARGE_SIZE: 42,
}


# =========================
# UI layout helpers
# =========================

def make_tool_buttons(button_font):
    """Create compact tool buttons in one clean row."""
    buttons = {}
    x = 18
    y = 34
    gap = 7
    button_height = 30
    max_row_width = WIDTH - 245

    for tool, label, shortcut in TOOL_LABELS:
        button_width = max(52, button_font.size(label)[0] + 16)

        # just in case screen gets smaller, it can wrap to next row
        if x + button_width > max_row_width:
            x = 18
            y += button_height + 8

        buttons[tool] = pygame.Rect(x, y, button_width, button_height)
        x += button_width + gap

    return buttons


def make_color_buttons():
    """Make color circle positions."""
    paint_colors = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
    color_buttons = []

    for i, color in enumerate(paint_colors):
        color_buttons.append((color, pygame.Rect(18 + i * 34, 111, 24, 24)))

    return color_buttons


def make_ui_controls():
    """Create remaining toolbar rects: current color, size, actions."""
    current_color_rect = pygame.Rect(305, 111, 48, 24)

    size_buttons = [
        ("S", SMALL_SIZE, pygame.Rect(390, 112, 34, 23)),
        ("M", MEDIUM_SIZE, pygame.Rect(431, 112, 34, 23)),
        ("L", LARGE_SIZE, pygame.Rect(472, 112, 34, 23)),
    ]

    action_button_y = 34
    undo_button = pygame.Rect(WIDTH - 206, action_button_y, 84, 30)
    clear_button = pygame.Rect(WIDTH - 112, action_button_y, 94, 30)
    save_button = pygame.Rect(WIDTH - 206, action_button_y + 40, 84, 30)

    return current_color_rect, size_buttons, undo_button, clear_button, save_button


def draw_text_center(screen, text, rect, text_color, text_font):
    """Draw text in the middle of a rect."""
    label = text_font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_button(screen, rect, label, button_font, active=False, disabled=False):
    """Draw button with hover/active state. Tiny UI polish here."""
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

    # fake shadow, simple but looks nicer
    shadow_rect = rect.copy()
    shadow_rect.move_ip(2, 2)
    pygame.draw.rect(screen, SOFT_SHADOW, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, fill_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    draw_text_center(screen, label, rect, text_color, button_font)


def draw_section_label(screen, text, pos, title_font):
    """Small gray section title."""
    label = title_font.render(text, True, DARK_GRAY)
    screen.blit(label, pos)


def draw_toolbar(
    screen,
    button_font,
    small_font,
    title_font,
    status_font,
    tool_buttons,
    color_buttons,
    current_color_rect,
    size_buttons,
    undo_button,
    clear_button,
    save_button,
    current_tool,
    current_color,
    brush_size,
    undo_stack,
    status_message,
    status_time,
):
    """Draw the full toolbar UI."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, PANEL, (8, 8, WIDTH - 16, TOOLBAR_HEIGHT - 16), border_radius=14)
    pygame.draw.rect(screen, PANEL_DARK, (8, 8, WIDTH - 16, TOOLBAR_HEIGHT - 16), 2, border_radius=14)
    pygame.draw.line(screen, BORDER, (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    # tools
    draw_section_label(screen, "Tools", (18, 12), title_font)
    for tool, label, shortcut in TOOL_LABELS:
        rect = tool_buttons[tool]
        draw_button(screen, rect, label, button_font, active=(current_tool == tool))

    # action buttons, right side
    draw_section_label(screen, "Actions", (WIDTH - 206, 12), title_font)
    draw_button(screen, undo_button, "Undo", button_font, disabled=(len(undo_stack) == 0))
    draw_button(screen, clear_button, "Clear", button_font)
    draw_button(screen, save_button, "Save", button_font)

    # colors
    draw_section_label(screen, "Colors", (18, 92), title_font)
    for color_value, rect in color_buttons:
        pygame.draw.circle(screen, color_value, rect.center, 12)
        pygame.draw.circle(screen, BORDER, rect.center, 13, 2)

        if color_value == current_color:
            pygame.draw.circle(screen, BLUE_ACCENT, rect.center, 17, 3)

    # current color preview
    draw_section_label(screen, "Current", (305, 92), title_font)
    pygame.draw.rect(screen, current_color, current_color_rect, border_radius=6)
    pygame.draw.rect(screen, BORDER, current_color_rect, 2, border_radius=6)

    # size buttons
    draw_section_label(screen, "Size", (390, 92), title_font)
    for label, size, rect in size_buttons:
        draw_button(screen, rect, label, button_font, active=(brush_size == size))

    # keep hint short so it doesn't crash into Actions panel
    hint = small_font.render(
        "Shortcuts: B/P/L/F/X/R/C/E/S/T/Q/H  •  1/2/3 size  •  Ctrl/Cmd+Z/S",
        True,
        DARK_GRAY,
    )
    screen.blit(hint, (535, 102))

    # status disappears back to Ready after a few secs
    message = status_message
    if pygame.time.get_ticks() - status_time > 3500:
        message = "Ready"

    status = status_font.render(message, True, DARK_GRAY)
    screen.blit(status, (535, 122))


# =========================
# canvas / drawing helpers
# =========================

def inside_canvas(pos):
    """Check if mouse is inside canvas area."""
    return CANVAS_RECT.collidepoint(pos)


def to_canvas_pos(pos):
    """Convert screen pos to canvas pos because toolbar takes top space."""
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)


def save_canvas(canvas):
    """Save canvas as png with timestamp, so files don't overwrite."""
    os.makedirs("assets", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"assets/paint_{timestamp}.png"

    pygame.image.save(canvas, filename)
    print(f"Canvas saved as {filename}")

    return filename


def flood_fill(surface, start_pos, fill_color):
    """
    Flood fill using get_at() and set_at().
    Exact color match only, as task allows.
    """
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return False

    target_color = surface.get_at((x, y))
    replacement_color = pygame.Color(fill_color[0], fill_color[1], fill_color[2])

    # no point filling if color is already same
    if target_color == replacement_color:
        return False

    stack = [(x, y)]

    while stack:
        px, py = stack.pop()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue

        # boundary check: if pixel color changed, stop there
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
    Draw continuous freehand stroke.
    We use draw.line + circles to avoid ugly gaps on large size.
    """
    radius = max(1, width // 2)

    x1, y1 = start
    x2, y2 = end
    distance = math.hypot(x2 - x1, y2 - y1)

    if distance == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    # required-ish part for pencil: line between old and new cursor pos
    pygame.draw.line(surface, color, start, end, width)

    # gap filler, esp useful for L size and fast mouse movement
    spacing = max(1, radius // 2)
    steps = max(1, int(distance / spacing))

    for i in range(steps + 1):
        t = i / steps
        x = round(x1 + (x2 - x1) * t)
        y = round(y1 + (y2 - y1) * t)
        pygame.draw.circle(surface, color, (x, y), radius)


# =========================
# shape helpers
# =========================

def get_square_rect(start, end):
    """Make a square rect based on drag direction."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    width = x2 - x1
    height = y2 - y1
    side = min(abs(width), abs(height))

    if width < 0:
        x1 -= side
    if height < 0:
        y1 -= side

    return pygame.Rect(x1, y1, side, side)


def get_right_triangle_points(start, end):
    """3 points for right triangle."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    return [
        (x1, y1),
        (x1, y2),
        (x2, y2),
    ]


def get_equilateral_triangle_points(start, end):
    """3 points for equilateral triangle."""
    x1, y1 = to_canvas_pos(start)
    x2, y2 = to_canvas_pos(end)

    side = x2 - x1
    triangle_height = abs(side) * math.sqrt(3) / 2

    if side < 0:
        left_x = x2
        right_x = x1
    else:
        left_x = x1
        right_x = x2

    # down drag = points up, up drag = points down
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
    """4 points for diamond/rhombus shape."""
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


def draw_shape(surface, tool, start, end, current_color, brush_size, offset_y=0):
    """
    Draw line/shape.
    offset_y is only for preview, because screen has toolbar but canvas doesn't.
    """
    if tool == LINE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        pygame.draw.line(surface, current_color, (x1, y1 + offset_y), (x2, y2 + offset_y), brush_size)

    elif tool == RECTANGLE:
        x1, y1 = to_canvas_pos(start)
        x2, y2 = to_canvas_pos(end)

        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
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


# =========================
# text helpers
# =========================

def get_text_font(brush_size):
    """Text font size follows S/M/L buttons too."""
    font_size = TEXT_FONT_SIZES.get(brush_size, 28)
    return pygame.font.SysFont("Arial", font_size)


def draw_text_preview(screen, typing_text, text_pos, text_content, current_color, brush_size):
    """Live preview while typing. Not permanent until Enter."""
    if not typing_text or text_pos is None:
        return

    text_font = get_text_font(brush_size)

    x, y = text_pos
    screen_x = x
    screen_y = y + TOOLBAR_HEIGHT

    text_surface = text_font.render(text_content, True, current_color)
    screen.blit(text_surface, (screen_x, screen_y))

    # blinking cursor, simple but useful
    current_time = pygame.time.get_ticks()
    if (current_time // 500) % 2 == 0:
        cursor_x = screen_x + text_surface.get_width() + 2
        cursor_top = screen_y
        cursor_bottom = screen_y + text_font.get_height()
        pygame.draw.line(screen, current_color, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)