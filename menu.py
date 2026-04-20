import math
import pygame
from constants import WIDTH, HEIGHT, INFO_HEIGHT, WHITE, GREY, GOLD, DARK_BG, RED, BLACK

WINDOW_H = HEIGHT + INFO_HEIGHT

DIFFICULTIES = [
    ("EASY",   2, (50,  175,  75),  "Beginner friendly · depth 2"),
    ("MEDIUM", 4, (215, 165,  35),  "A solid challenge  · depth 4"),
    ("HARD",   6, (205,  50,  50),  "Brutal opponent    · depth 6"),
]

BTN_W, BTN_H = 420, 72
BTN_X = (WIDTH - BTN_W) // 2
BTN_GAP = 18


# ----------------------------------------------------------------- helpers

def _draw_shadow_text(surf, font, text, color, x, y, shadow_offset=3):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + shadow_offset, y + shadow_offset))
    surf.blit(font.render(text, True, color),     (x, y))


def _draw_divider_line(surf, cx, y, half_width, color):
    pygame.draw.line(surf, color, (cx - half_width, y), (cx - 40, y), 1)
    pygame.draw.line(surf, color, (cx + 40,         y), (cx + half_width, y), 1)


def _draw_piece_icon(surf, cx, cy, radius, color, rim_color):
    shadow = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 80), (radius + 4, radius + 6), radius)
    surf.blit(shadow, (cx - radius - 4, cy - radius - 2))
    pygame.draw.circle(surf, rim_color, (cx, cy), radius + 2)
    pygame.draw.circle(surf, color,     (cx, cy), radius)
    lighter = tuple(min(255, c + 40) for c in color)
    pygame.draw.circle(surf, lighter,   (cx - 2, cy - 2), radius - 5)
    shine = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shine, (255, 255, 255, 50),
                        (radius // 3, radius // 5, radius * 3 // 4, radius * 2 // 5))
    surf.blit(shine, (cx - radius, cy - radius))


def _build_assets():
    """One-time setup: fonts, button rects, vignette surface."""
    fonts = {
        "title": pygame.font.SysFont("segoeui", 72, bold=True),
        "sub":   pygame.font.SysFont("segoeui", 20),
        "sect":  pygame.font.SysFont("segoeui", 16),
        "btn":   pygame.font.SysFont("segoeui", 28, bold=True),
        "desc":  pygame.font.SysFont("segoeui", 17),
    }

    total_h = len(DIFFICULTIES) * BTN_H + (len(DIFFICULTIES) - 1) * BTN_GAP
    start_y = WINDOW_H // 2 - total_h // 2 + 55
    buttons = []
    for i, (label, depth, color, desc) in enumerate(DIFFICULTIES):
        y = start_y + i * (BTN_H + BTN_GAP)
        buttons.append((pygame.Rect(BTN_X, y, BTN_W, BTN_H), depth, label, color, desc))

    vignette = pygame.Surface((WIDTH, WINDOW_H), pygame.SRCALPHA)
    cx_v, cy_v = WIDTH // 2, WINDOW_H // 2
    for ring in range(60, 0, -1):
        alpha  = int(120 * (1 - ring / 60) ** 1.8)
        radius = int(max(WIDTH, WINDOW_H) * ring / 60)
        pygame.draw.circle(vignette, (0, 0, 0, alpha), (cx_v, cy_v), radius, 30)

    return fonts, buttons, vignette


def render_menu_frame(win, fonts, buttons, vignette, mouse_pos=(0, 0)):
    """Draw one complete menu frame onto `win`. Does NOT call display.flip()."""
    f = fonts

    # Background
    win.fill(DARK_BG)
    dot_spacing = 28
    for gy in range(0, WINDOW_H, dot_spacing):
        for gx in range(0, WIDTH, dot_spacing):
            pygame.draw.circle(win, (30, 30, 48), (gx, gy), 1)
    win.blit(vignette, (0, 0))

    # Decorative piece icons
    for ix, iy, col, rim in [
        (120, 140, RED,   (230, 80, 80)),
        (680, 140, BLACK, (90, 90, 115)),
        (100, 500, BLACK, (90, 90, 115)),
        (700, 500, RED,   (230, 80, 80)),
    ]:
        _draw_piece_icon(win, ix, iy, 22, col, rim)

    # Title
    tx = WIDTH // 2 - f["title"].render("CHECKERS", True, GOLD).get_width() // 2
    _draw_shadow_text(win, f["title"], "CHECKERS", GOLD, tx, 80, shadow_offset=3)

    # Subtitle
    sub = f["sub"].render("Minimax  ·  Alpha-Beta Pruning", True, (170, 155, 125))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 165))
    pygame.draw.line(win, (100, 75, 10), (WIDTH // 2 - 180, 193), (WIDTH // 2 + 180, 193), 1)

    # Section header
    start_y = buttons[0][0].y
    sect_y  = start_y - 36
    sect    = f["sect"].render("CHOOSE DIFFICULTY", True, (140, 130, 110))
    win.blit(sect, (WIDTH // 2 - sect.get_width() // 2, sect_y))
    _draw_divider_line(win, WIDTH // 2, sect_y + 9, 210, (80, 70, 50))

    # Buttons
    for rect, depth, label, color, desc in buttons:
        hovered = rect.collidepoint(mouse_pos)

        shadow_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_s, (0, 0, 0, 100), (0, 0, rect.w, rect.h), border_radius=14)
        win.blit(shadow_s, (rect.x + 5, rect.y + 5))

        bg_col = (45, 45, 70) if hovered else (35, 35, 55)
        pygame.draw.rect(win, bg_col, rect, border_radius=14)

        accent_col = tuple(min(255, int(c * 1.15)) for c in color) if hovered else color
        pygame.draw.rect(win, accent_col,
                         pygame.Rect(rect.x, rect.y, 8, rect.h),
                         border_top_left_radius=14, border_bottom_left_radius=14)

        border_s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(border_s, (*color, 220 if hovered else 100),
                         (0, 0, rect.w, rect.h), 2, border_radius=14)
        win.blit(border_s, rect.topleft)

        win.blit(f["btn"].render(label, True, WHITE if hovered else (210, 210, 210)),
                 (rect.x + 24, rect.y + 10))
        win.blit(f["desc"].render(desc, True, (165, 165, 180)),
                 (rect.x + 24, rect.y + 42))

        if hovered:
            arrow = f["btn"].render("›", True, tuple(min(255, c + 60) for c in color))
            win.blit(arrow, (rect.right - arrow.get_width() - 18,
                             rect.centery - arrow.get_height() // 2))

    # Footer
    footer = f["sect"].render(
        "You play  RED  ·  AI plays  BLACK  ·  R = back to menu", True, (85, 80, 100))
    win.blit(footer, (WIDTH // 2 - footer.get_width() // 2, WINDOW_H - 32))


def show_menu(win):
    """Event loop: renders menu frames until the user picks a difficulty."""
    pygame.font.init()
    fonts, buttons, vignette = _build_assets()
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, depth, *_ in buttons:
                    if rect.collidepoint(mouse_pos):
                        return depth

        render_menu_frame(win, fonts, buttons, vignette, mouse_pos)
        pygame.display.flip()
