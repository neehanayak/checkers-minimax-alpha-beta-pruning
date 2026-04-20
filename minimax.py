from constants import RED, BLACK, ROWS, COLS

# RED maximises; BLACK minimises (AI plays BLACK).

# ----------------------------------------------------------------- public API

def minimax(board, depth, max_player,
            alpha=float('-inf'), beta=float('inf')):
    """
    Minimax with alpha-beta pruning.
    Returns (score, best_board_state).

    alpha — best score MAX can already guarantee (prune when beta <= alpha)
    beta  — best score MIN can already guarantee (prune when beta <= alpha)
    """
    if depth == 0 or board.winner() is not None:
        return _evaluate(board), board

    if max_player:                          # RED — maximise
        best_score = float('-inf')
        best_state = None
        for state in _get_all_moves(board, RED):
            score, _ = minimax(state, depth - 1, False, alpha, beta)
            if score > best_score:
                best_score = score
                best_state = state
            alpha = max(alpha, best_score)
            if beta <= alpha:               # β-cutoff — MIN won't allow this
                break
        return best_score, best_state

    else:                                   # BLACK — minimise
        best_score = float('inf')
        best_state = None
        for state in _get_all_moves(board, BLACK):
            score, _ = minimax(state, depth - 1, True, alpha, beta)
            if score < best_score:
                best_score = score
                best_state = state
            beta = min(beta, best_score)
            if beta <= alpha:               # α-cutoff — MAX won't allow this
                break
        return best_score, best_state


# ----------------------------------------------------------------- evaluation

# Per-square positional weights (higher = more desirable).
# Centre squares offer better mobility; edge squares are traps.
_POS_WEIGHT = [
    [0.0, 0.3, 0.0, 0.3, 0.0, 0.3, 0.0, 0.3],
    [0.3, 0.0, 0.4, 0.0, 0.4, 0.0, 0.3, 0.0],
    [0.0, 0.4, 0.0, 0.5, 0.0, 0.5, 0.0, 0.3],
    [0.3, 0.0, 0.5, 0.0, 0.5, 0.0, 0.4, 0.0],
    [0.0, 0.4, 0.0, 0.5, 0.0, 0.5, 0.0, 0.3],
    [0.3, 0.0, 0.5, 0.0, 0.5, 0.0, 0.4, 0.0],
    [0.0, 0.4, 0.0, 0.4, 0.0, 0.4, 0.0, 0.3],
    [0.3, 0.0, 0.3, 0.0, 0.3, 0.0, 0.3, 0.0],
]


def _evaluate(board):
    """
    Combines four factors:
      1. Material  — piece count (kings worth 1.5×)
      2. Position  — centre-square bonuses
      3. Mobility  — number of available moves (rewarded)
      4. Advancement — non-kings rewarded for moving toward promotion
    Positive → good for RED.  Negative → good for BLACK.
    """
    if board.winner() == RED:
        return float('inf')
    if board.winner() == BLACK:
        return float('-inf')

    red_score = black_score = 0.0

    for r in range(ROWS):
        for c in range(COLS):
            piece = board.board[r][c]
            if piece == 0:
                continue

            # 1. Material
            val = 1.5 if piece.king else 1.0

            # 2. Position
            val += _POS_WEIGHT[r][c]

            # 3. Advancement (non-kings only)
            if not piece.king:
                if piece.color == RED:
                    val += (ROWS - 1 - r) * 0.05   # reward moving up
                else:
                    val += r * 0.05                 # reward moving down

            if piece.color == RED:
                red_score += val
            else:
                black_score += val

    # 4. Mobility — count legal moves available to each side
    red_mobility   = sum(len(board.get_valid_moves(p))
                         for p in board.get_all_pieces(RED))
    black_mobility = sum(len(board.get_valid_moves(p))
                         for p in board.get_all_pieces(BLACK))
    red_score   += red_mobility   * 0.1
    black_score += black_mobility * 0.1

    return red_score - black_score


# ---------------------------------------------------------- move generation

def _get_all_moves(board, color):
    """
    Returns board copies after every legal move for `color`.
    Mandatory-capture rule enforced: if any capture exists, only captures returned.
    Captures are placed first for better alpha-beta move ordering.
    """
    candidates = []
    for piece in board.get_all_pieces(color):
        for dest, skipped in board.get_valid_moves(piece).items():
            candidates.append((piece, dest, skipped))

    # Enforce + move-order: captures before quiet moves
    captures = [(p, d, s) for p, d, s in candidates if s]
    if captures:
        candidates = captures
    else:
        # No captures — sort quiet moves by positional weight (best first)
        candidates.sort(
            key=lambda t: _POS_WEIGHT[t[1][0]][t[1][1]], reverse=True
        )

    states = []
    for piece, (row, col), skipped in candidates:
        tmp = board.copy()
        tmp_piece = tmp.get_piece(piece.row, piece.col)
        _apply_move(tmp, tmp_piece, row, col, skipped)
        states.append(tmp)

    return states


def _apply_move(board, piece, row, col, skipped):
    board.move(piece, row, col)
    if skipped:
        to_remove = [board.get_piece(p.row, p.col) for p in skipped]
        board.remove(to_remove)
