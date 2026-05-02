import pygame
import sys

# all helper funcs + constants are in tools.py now, so main.py stays cleaner
from tools import *

# init pygame first, otherwise fonts/window can act weird
pygame.init()

# basic window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# fonts for UI stuff
font = pygame.font.SysFont("Arial", 16)
button_font = pygame.font.SysFont("Arial", 15)
small_font = pygame.font.SysFont("Arial", 12)
title_font = pygame.font.SysFont("Arial", 13, bold=True)
status_font = pygame.font.SysFont("Arial", 14)

# this is the actual drawing surface
# btw we draw on canvas, then blit it to screen every frame
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# toolbar / UI rectangles
tool_buttons = make_tool_buttons(button_font)
color_buttons = make_color_buttons()
current_color_rect, size_buttons, undo_button, clear_button, save_button = make_ui_controls()

# selected options
current_tool = BRUSH
current_color = BLACK
brush_size = MEDIUM_SIZE

# little status text in toolbar
status_message = "Ready"
status_time = 0

# drawing state vars
drawing = False
start_pos = None
last_pos = None
current_pos = None

# text tool state
typing_text = False
text_pos = None
text_content = ""

# undo history
undo_stack = []
MAX_UNDO = 25


def set_status(message):
    """Shows small msg in toolbar, like 'saved' or 'selected brush'."""
    global status_message, status_time
    status_message = message
    status_time = pygame.time.get_ticks()


def save_undo():
    """Save canvas copy before changing it. Kinda like mini history."""
    undo_stack.append(canvas.copy())

    # no need to keep infinite history, 25 is enough imo
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)


def undo():
    """Restore previous canvas state."""
    if undo_stack:
        previous_canvas = undo_stack.pop()
        canvas.blit(previous_canvas, (0, 0))
        set_status("Undo applied")
    else:
        set_status("Nothing to undo")


def draw_preview():
    """Temporary preview for line/shapes while dragging."""
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
        # clip it so preview does not go on toolbar area
        old_clip = screen.get_clip()
        screen.set_clip(CANVAS_RECT)
        draw_shape(screen, current_tool, start_pos, current_pos, current_color, brush_size, TOOLBAR_HEIGHT)
        screen.set_clip(old_clip)


def confirm_text():
    """Put typed text permanently onto canvas."""
    global typing_text, text_pos, text_content

    if text_pos is not None and text_content != "":
        save_undo()
        text_font = get_text_font(brush_size)
        text_surface = text_font.render(text_content, True, current_color)
        canvas.blit(text_surface, text_pos)
        set_status("Text added")

    typing_text = False
    text_pos = None
    text_content = ""


def cancel_text():
    """Cancel text mode without drawing anything."""
    global typing_text, text_pos, text_content

    typing_text = False
    text_pos = None
    text_content = ""
    set_status("Text cancelled")


def handle_toolbar_click(mouse_pos):
    """
    Handles toolbar buttons.
    Returns True if user clicked toolbar, so canvas should not draw.
    """
    global current_tool, current_color, brush_size

    # select tools
    for tool, rect in tool_buttons.items():
        if rect.collidepoint(mouse_pos):
            current_tool = tool
            set_status(f"Selected {tool}")
            return True

    # select colors
    for color_value, rect in color_buttons:
        if rect.collidepoint(mouse_pos):
            current_color = color_value
            set_status("Color changed")
            return True

    # select S/M/L size
    for label, size, rect in size_buttons:
        if rect.collidepoint(mouse_pos):
            brush_size = size
            set_status(f"Size: {label}")
            return True

    # actions
    if undo_button.collidepoint(mouse_pos):
        undo()
        return True

    if clear_button.collidepoint(mouse_pos):
        save_undo()
        canvas.fill(WHITE)
        set_status("Canvas cleared")
        return True

    if save_button.collidepoint(mouse_pos):
        filename = save_canvas(canvas)
        set_status(f"Saved: {filename}")
        return True

    # any other toolbar click should still block drawing
    return mouse_pos[1] < TOOLBAR_HEIGHT


# main loop
while True:
    for event in pygame.event.get():

        # close window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # keyboard stuff
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            # when text tool is active, keyboard means text input first
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

            # undo: Ctrl+Z / Cmd+Z
            elif event.key == pygame.K_z and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                undo()

            # save: Ctrl+S / Cmd+S
            elif event.key == pygame.K_s and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                filename = save_canvas(canvas)
                set_status(f"Saved: {filename}")

            # size shortcuts
            elif event.key == pygame.K_1:
                brush_size = SMALL_SIZE
                set_status("Size: Small")
            elif event.key == pygame.K_2:
                brush_size = MEDIUM_SIZE
                set_status("Size: Medium")
            elif event.key == pygame.K_3:
                brush_size = LARGE_SIZE
                set_status("Size: Large")

            # tool shortcuts
            elif event.key == pygame.K_b:
                current_tool = BRUSH
                set_status("Selected brush")
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

        # mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # toolbar clicks should not draw on canvas
            if handle_toolbar_click(mouse_pos):
                continue

            if inside_canvas(mouse_pos):

                # text tool: click sets cursor position
                if current_tool == TEXT:
                    typing_text = True
                    text_pos = to_canvas_pos(mouse_pos)
                    text_content = ""
                    set_status("Typing text: Enter confirms, Escape cancels")
                    continue

                # fill tool: one click fill
                if current_tool == FILL:
                    canvas_pos = to_canvas_pos(mouse_pos)
                    replacement = pygame.Color(current_color[0], current_color[1], current_color[2])

                    # don't waste undo if nothing changes
                    if canvas.get_at(canvas_pos) != replacement:
                        save_undo()
                        flood_fill(canvas, canvas_pos, current_color)
                        set_status("Area filled")
                    else:
                        set_status("Area already has this color")

                    continue

                # normal drawing / shape start
                drawing = True
                start_pos = mouse_pos
                current_pos = mouse_pos
                last_pos = to_canvas_pos(mouse_pos)

                # save undo before freehand tools start changing pixels
                if current_tool in [BRUSH, PENCIL, ERASER]:
                    save_undo()

                # draw first dot so single-click drawing works too
                if current_tool == BRUSH:
                    draw_smooth_stroke(canvas, current_color, last_pos, last_pos, brush_size)
                elif current_tool == PENCIL:
                    draw_smooth_stroke(canvas, current_color, last_pos, last_pos, brush_size)
                elif current_tool == ERASER:
                    draw_smooth_stroke(canvas, WHITE, last_pos, last_pos, brush_size)

        # mouse drag
        if event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                current_pos = event.pos
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool == BRUSH:
                    draw_smooth_stroke(canvas, current_color, last_pos, canvas_pos, brush_size)
                elif current_tool == PENCIL:
                    draw_smooth_stroke(canvas, current_color, last_pos, canvas_pos, brush_size)
                elif current_tool == ERASER:
                    draw_smooth_stroke(canvas, WHITE, last_pos, canvas_pos, brush_size)

                last_pos = canvas_pos

        # mouse release
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

                # final shape gets drawn only after releasing mouse
                if current_tool in shape_tools and inside_canvas(end_pos):
                    save_undo()
                    draw_shape(canvas, current_tool, start_pos, end_pos, current_color, brush_size)

            # reset drawing vars
            drawing = False
            start_pos = None
            current_pos = None
            last_pos = None

    # redraw everything
    screen.fill(CANVAS_BG)

    draw_toolbar(
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
    )

    # canvas area
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    pygame.draw.rect(screen, BORDER, CANVAS_RECT, 2)

    # previews are drawn on screen only, not saved to canvas yet
    draw_preview()
    draw_text_preview(screen, typing_text, text_pos, text_content, current_color, brush_size)

    pygame.display.flip()
    clock.tick(60)