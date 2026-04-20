import pygame
from constants import WIDTH, HEIGHT, INFO_HEIGHT, SQUARE_SIZE
from game import Game, AI_COLOR
from menu import show_menu

FPS = 60
AI_DELAY_MS = 700


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT + INFO_HEIGHT))
    pygame.display.set_caption("Checkers — Minimax AI")
    clock = pygame.time.Clock()

    while True:
        # ── difficulty menu ──────────────────────────────────────────────────
        depth = show_menu(win)
        if depth is None:           # window closed on menu
            break

        # ── game loop ────────────────────────────────────────────────────────
        game       = Game(win, depth)
        ai_move_at = None

        running = True
        while running:
            clock.tick(FPS)

            # AI turn — show "thinking" for AI_DELAY_MS then compute
            if not game.game_over and game.turn == AI_COLOR:
                now = pygame.time.get_ticks()
                if ai_move_at is None:
                    ai_move_at = now + AI_DELAY_MS
                elif now >= ai_move_at:
                    ai_move_at = None
                    game.ai_move()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return                      # exit entirely
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        running = False         # return to menu
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = get_row_col_from_mouse(pygame.mouse.get_pos())
                    game.select(row, col)

            game.update()

    pygame.quit()


if __name__ == "__main__":
    main()
