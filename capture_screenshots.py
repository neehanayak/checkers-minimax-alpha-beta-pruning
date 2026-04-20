"""
Run once to generate screenshots used in README.md:
    python capture_screenshots.py
Saves three PNGs into screenshots/
"""
import os
import pygame

os.makedirs("screenshots", exist_ok=True)
pygame.init()

from constants import WIDTH, HEIGHT, INFO_HEIGHT, RED, BLACK, SQUARE_SIZE
from board import Board, Piece
from game import Game
from menu import _build_assets, render_menu_frame

WINDOW_H = HEIGHT + INFO_HEIGHT
win = pygame.display.set_mode((WIDTH, WINDOW_H))
pygame.display.set_caption("Screenshot capture")


# ── 1. Menu ──────────────────────────────────────────────────────────────────
fonts, buttons, vignette = _build_assets()
# Simulate hovering over the MEDIUM button for a more interesting screenshot
hover_pos = (buttons[1][0].centerx, buttons[1][0].centery)
render_menu_frame(win, fonts, buttons, vignette, mouse_pos=hover_pos)
pygame.display.flip()
pygame.image.save(win, "screenshots/menu.png")
print("Saved screenshots/menu.png")


# ── 2. Mid-game board ────────────────────────────────────────────────────────
game = Game(win, depth=4)
b    = game.board

# Clear the auto-generated board and set a custom mid-game position
for r in range(8):
    for c in range(8):
        b.board[r][c] = 0

def place(row, col, color, king=False):
    p = Piece(row, col, color)
    if king:
        p.king = True
    b.board[row][col] = p

# Black pieces (top)
place(0, 3, BLACK)
place(0, 5, BLACK)
place(1, 2, BLACK)
place(1, 6, BLACK)
place(2, 5, BLACK)
place(3, 0, BLACK)
place(3, 4, BLACK, king=True)

# Red pieces (bottom)
place(4, 3, RED)
place(5, 2, RED)
place(5, 6, RED)
place(6, 1, RED, king=True)
place(6, 5, RED)
place(7, 4, RED)

# Update counts to match
b.black_left  = sum(1 for r in b.board for p in r if p != 0 and p.color == BLACK)
b.red_left    = sum(1 for r in b.board for p in r if p != 0 and p.color == RED)
b.black_kings = sum(1 for r in b.board for p in r if p != 0 and p.color == BLACK and p.king)
b.red_kings   = sum(1 for r in b.board for p in r if p != 0 and p.color == RED   and p.king)

# Select a red piece so valid-move dots show
red_piece = b.get_piece(5, 2)
game.selected    = red_piece
game.valid_moves = b.get_valid_moves(red_piece)
game.last_ai_dest = (3, 4)   # highlight the king the AI just moved to

game.update()
pygame.image.save(win, "screenshots/gameplay.png")
print("Saved screenshots/gameplay.png")


# ── 3. Game-over screen ───────────────────────────────────────────────────────
game2 = Game(win, depth=4)
game2.game_over = True
game2._winner   = BLACK       # AI wins

# Re-use the same board so the background looks realistic
game2.board = game.board
game2.last_ai_dest = None
game2.selected     = None
game2.valid_moves  = {}
game2.update()
pygame.image.save(win, "screenshots/gameover.png")
print("Saved screenshots/gameover.png")


pygame.quit()
print("\nDone — screenshots are in the screenshots/ folder.")
