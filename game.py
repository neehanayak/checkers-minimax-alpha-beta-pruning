import math
import pygame
from board import Board
from minimax import minimax
from constants import (
    RED, BLACK, WHITE, GREY, GOLD, GREEN, BLUE, AMBER, DARK_BG,
    SQUARE_SIZE, WIDTH, HEIGHT, INFO_HEIGHT
)

AI_COLOR = BLACK

FONT_LARGE = FONT_MED = FONT_SMALL = None


def _init_fonts():
    global FONT_LARGE, FONT_MED, FONT_SMALL
    if FONT_LARGE is None:
        FONT_LARGE = pygame.font.SysFont("segoeui", 34, bold=True)
        FONT_MED   = pygame.font.SysFont("segoeui", 22)
        FONT_SMALL = pygame.font.SysFont("segoeui", 17)


_DEPTH_LABEL = {2: "Easy", 4: "Medium", 6: "Hard"}


class Game:
    def __init__(self, win, depth=6):
        self.win   = win
        self.depth = depth
        self._init()

    def _init(self):
        self.selected     = None
        self.board        = Board()
        self.turn         = RED
        self.valid_moves  = {}
        self.game_over    = False
        self._winner      = None
        self.last_ai_dest = None

    def reset(self):
        self._init()

    # ---------------------------------------------------------------- drawing
    def update(self):
        _init_fonts()
        self.board.draw(self.win, self.valid_moves)
        self._draw_last_ai_move()
        self._draw_selected()
        self._draw_status_bar()
        if self.game_over:
            self._draw_game_over()
        pygame.display.flip()

    def _draw_last_ai_move(self):
        if self.last_ai_dest is None:
            return
        r, c = self.last_ai_dest
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        surf.fill((255, 170, 0, 55))
        self.win.blit(surf, (c * SQUARE_SIZE, r * SQUARE_SIZE))
        pygame.draw.rect(self.win, AMBER,
                         (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    def _draw_selected(self):
        if not self.selected:
            return
        t     = pygame.time.get_ticks() / 1000
        alpha = int(160 + 90 * math.sin(t * 4))   # pulsing 70-250
        x = self.selected.col * SQUARE_SIZE
        y = self.selected.row * SQUARE_SIZE
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*BLUE, alpha),
                         (0, 0, SQUARE_SIZE, SQUARE_SIZE), 4, border_radius=4)
        self.win.blit(surf, (x, y))

    def _draw_status_bar(self):
        bar_y = HEIGHT
        bar_h = INFO_HEIGHT
        pygame.draw.rect(self.win, (16, 16, 28), (0, bar_y, WIDTH, bar_h))

        # Top separator — two-tone line
        pygame.draw.line(self.win, (55, 38, 15),  (0, bar_y),     (WIDTH, bar_y),     2)
        pygame.draw.line(self.win, (85, 60, 25),  (0, bar_y + 2), (WIDTH, bar_y + 2), 1)

        b = self.board

        # ── left: black (AI) piece count ─────────────────────────────────
        self._draw_piece_counter(20, bar_y + 18, BLACK, (90, 90, 115),
                                 f"AI   ×{b.black_left}", b.black_kings)

        # ── centre: turn label ───────────────────────────────────────────
        if self.turn == AI_COLOR and not self.game_over:
            dots  = "." * (1 + (pygame.time.get_ticks() // 350) % 3)
            label = f"AI thinking{dots}"
            color = (210, 200, 65)
        elif self.turn == RED:
            label, color = "Your turn", (215, 70, 70)
        else:
            label, color = "AI's turn", (190, 190, 210)

        turn_surf = FONT_LARGE.render(label, True, color)
        self.win.blit(turn_surf,
                      (WIDTH // 2 - turn_surf.get_width() // 2, bar_y + 28))

        # ── right: red (you) piece count ─────────────────────────────────
        red_label = f"You  ×{b.red_left}"
        rw = FONT_MED.render(red_label, True, WHITE).get_width() + 36
        self._draw_piece_counter(WIDTH - rw - 16, bar_y + 18, RED, (230, 80, 80),
                                 red_label, b.red_kings)

        # ── bottom-right: difficulty + hint ──────────────────────────────
        diff  = _DEPTH_LABEL.get(self.depth, f"depth {self.depth}")
        hint  = FONT_SMALL.render(f"{diff}  ·  R = menu", True, (80, 75, 100))
        self.win.blit(hint, (WIDTH - hint.get_width() - 16, bar_y + 64))

    def _draw_piece_counter(self, x, y, piece_color, rim_color, label, kings):
        # Small piece icon
        pygame.draw.circle(self.win, rim_color,   (x + 12, y + 10), 11)
        pygame.draw.circle(self.win, piece_color, (x + 12, y + 10), 9)
        lighter = tuple(min(255, c + 40) for c in piece_color)
        pygame.draw.circle(self.win, lighter,     (x + 10, y + 8),  5)

        lbl  = FONT_MED.render(label, True, (215, 215, 215))
        self.win.blit(lbl, (x + 28, y + 2))

        if kings:
            king_txt = FONT_SMALL.render(f"♛ {kings}", True, (220, 195, 40))
            self.win.blit(king_txt, (x + 28, y + 28))

    def _draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 8, 18, 185))
        self.win.blit(overlay, (0, 0))

        if self._winner == RED:
            title, title_col = "YOU  WIN!", (230, 80,  80)
        else:
            title, title_col = "AI  WINS!", (130, 130, 255)

        # Shadow
        shadow_surf = FONT_LARGE.render(title, True, (0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 2
        self.win.blit(shadow_surf,
                      (cx - shadow_surf.get_width() // 2 + 3, cy - 38 + 3))

        # Title
        title_surf = FONT_LARGE.render(title, True, title_col)
        self.win.blit(title_surf, (cx - title_surf.get_width() // 2, cy - 38))

        # Decorative line
        pygame.draw.line(self.win, title_col,
                         (cx - 120, cy + 4), (cx + 120, cy + 4), 1)

        # Sub-text
        sub = FONT_MED.render("Press  R  to return to menu", True, (170, 165, 185))
        self.win.blit(sub, (cx - sub.get_width() // 2, cy + 20))

    # --------------------------------------------------------------- AI move
    def ai_move(self):
        old_pos = {(p.row, p.col) for p in self.board.get_all_pieces(BLACK)}
        _, new_board = minimax(self.board, self.depth, max_player=False)
        if new_board:
            new_pos = {(p.row, p.col) for p in new_board.get_all_pieces(BLACK)}
            arrived = new_pos - old_pos
            self.last_ai_dest = next(iter(arrived)) if arrived else None
            self.board = new_board
            self._change_turn()

    # ------------------------------------------------------------- selection
    def select(self, row, col):
        if self.game_over or self.turn == AI_COLOR:
            return
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        if self.selected:
            if not self._move(row, col):
                self.selected    = None
                self.valid_moves = {}
                self.select(row, col)
            return
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected    = piece
            self.valid_moves = self.board.get_valid_moves(piece)

    def _move(self, row, col):
        if self.selected and (row, col) in self.valid_moves:
            captured = self.valid_moves[(row, col)]
            self.board.move(self.selected, row, col)
            if captured:
                self.board.remove(captured)
            self._change_turn()
            return True
        return False

    def _change_turn(self):
        self.valid_moves = {}
        self.selected    = None
        self.turn = BLACK if self.turn == RED else RED
        w = self.board.winner()
        if w:
            self.game_over = True; self._winner = w; return
        if not any(self.board.get_valid_moves(p)
                   for p in self.board.get_all_pieces(self.turn)):
            self.game_over = True
            self._winner   = BLACK if self.turn == RED else RED

    def get_board(self):
        return self.board

    def winner(self):
        return self._winner
