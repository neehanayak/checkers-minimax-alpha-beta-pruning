import math
import pygame
from constants import (
    ROWS, COLS, SQUARE_SIZE,
    BROWN, CREAM, RED, BLACK, WHITE, GREY, GOLD, GREEN, BLUE, AMBER
)


# ----------------------------------------------------------------- helpers

def _draw_star(surf, cx, cy, outer_r, inner_r, color):
    pts = []
    for i in range(10):
        angle = math.pi / 5 * i - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, (200, 155, 0), pts, 1)


# ----------------------------------------------------------------- Piece

class Piece:
    PADDING = 11

    def __init__(self, row, col, color):
        self.row   = row
        self.col   = col
        self.color = color
        self.king  = False
        self.x = self.y = 0
        self._calc_pos()

    def _calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        r = SQUARE_SIZE // 2 - self.PADDING   # piece radius

        # ── drop shadow (alpha surface) ──────────────────────────────────
        shadow = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 90), (r + 6, r + 9), r)
        win.blit(shadow, (self.x - r - 6, self.y - r - 3))

        # ── rim ──────────────────────────────────────────────────────────
        if self.color == RED:
            rim = (230, 80, 80)
        else:
            rim = (90, 90, 115)
        pygame.draw.circle(win, rim, (self.x, self.y), r + 3)

        # ── main body ────────────────────────────────────────────────────
        pygame.draw.circle(win, self.color, (self.x, self.y), r)

        # ── inner lighter zone (3-D illusion) ────────────────────────────
        lighter = tuple(min(255, c + 45) for c in self.color)
        pygame.draw.circle(win, lighter, (self.x - 3, self.y - 3), r - 7)

        # ── shine highlight ───────────────────────────────────────────────
        shine = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shine, (255, 255, 255, 55),
            (r // 3, r // 5, r * 3 // 4, r * 2 // 5)
        )
        win.blit(shine, (self.x - r, self.y - r))

        # ── king star ─────────────────────────────────────────────────────
        if self.king:
            _draw_star(win, self.x, self.y, r - 5, (r - 5) // 2, GOLD)

    def move(self, row, col):
        self.row = row
        self.col = col
        self._calc_pos()


# ----------------------------------------------------------------- Board

class Board:
    def __init__(self):
        self.board      = []
        self.red_left   = self.black_left  = 12
        self.red_kings  = self.black_kings = 0
        self._create_board()

    # ---------------------------------------------------------------- setup
    def _create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    # --------------------------------------------------------------- drawing
    def draw_squares(self, win):
        win.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                pygame.draw.rect(win, CREAM, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                # Subtle top-edge highlight on light squares
                pygame.draw.line(win, (255, 235, 195), (x, y), (x + SQUARE_SIZE, y))
                pygame.draw.line(win, (255, 235, 195), (x, y), (x, y + SQUARE_SIZE))

        # Board border frame
        pygame.draw.rect(win, (55, 30, 8), (0, 0, SQUARE_SIZE * COLS, SQUARE_SIZE * ROWS), 5)

    def draw(self, win, valid_moves=None):
        self.draw_squares(win)
        if valid_moves:
            self._highlight_moves(win, valid_moves)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def _highlight_moves(self, win, valid_moves):
        for (row, col) in valid_moves:
            cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = row * SQUARE_SIZE + SQUARE_SIZE // 2
            # Semi-transparent fill
            fill = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(fill, (65, 210, 95, 55),
                               (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 4)
            win.blit(fill, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # Crisp ring
            pygame.draw.circle(win, GREEN, (cx, cy), SQUARE_SIZE // 4, 3)
            # Centre dot
            pygame.draw.circle(win, GREEN, (cx, cy), 5)

    # ------------------------------------------------------------- accessors
    def get_piece(self, row, col):
        return self.board[row][col]

    def get_all_pieces(self, color):
        return [p for row in self.board for p in row
                if p != 0 and p.color == color]

    # --------------------------------------------------------------- moves
    def get_valid_moves(self, piece):
        moves      = {}
        directions = self._directions(piece)
        captures   = self._get_captures(piece, piece.row, piece.col,
                                        piece.color, directions, [])
        if captures:
            return captures
        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == 0:
                moves[(r, c)] = []
        return moves

    def _directions(self, piece):
        if piece.king:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [(-1, -1), (-1, 1)] if piece.color == RED else [(1, -1), (1, 1)]

    def _get_captures(self, piece, row, col, color, directions, skipped):
        moves = {}
        for dr, dc in directions:
            mr, mc   = row + dr, col + dc
            lr, lc   = row + 2 * dr, col + 2 * dc
            if not (0 <= lr < ROWS and 0 <= lc < COLS):
                continue
            mid = self.board[mr][mc]
            if (mid != 0 and mid.color != color
                    and mid not in skipped
                    and self.board[lr][lc] == 0):
                new_skip = skipped + [mid]
                further  = self._get_captures(piece, lr, lc, color, directions, new_skip)
                if further:
                    for dest, chain in further.items():
                        moves[dest] = new_skip + [p for p in chain if p not in new_skip]
                else:
                    moves[(lr, lc)] = new_skip
        return moves

    # --------------------------------------------------------------- actions
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = \
            self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        if row == 0 and piece.color == RED:
            piece.make_king(); self.red_kings += 1
        if row == ROWS - 1 and piece.color == BLACK:
            piece.make_king(); self.black_kings += 1

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == RED:
                self.red_left  -= 1
                if piece.king: self.red_kings  -= 1
            else:
                self.black_left -= 1
                if piece.king: self.black_kings -= 1

    def copy(self):
        new = Board.__new__(Board)
        new.red_left = self.red_left; new.black_left  = self.black_left
        new.red_kings = self.red_kings; new.black_kings = self.black_kings
        new.board = []
        for row in self.board:
            new_row = []
            for p in row:
                if p == 0:
                    new_row.append(0)
                else:
                    cp = Piece(p.row, p.col, p.color); cp.king = p.king
                    new_row.append(cp)
            new.board.append(new_row)
        return new

    def winner(self):
        if self.red_left   <= 0: return BLACK
        if self.black_left <= 0: return RED
        return None
