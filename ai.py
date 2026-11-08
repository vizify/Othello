import random
import threading

from constants import EMPTY, N

BASE_WEIGHTS = [
    [100, -20, 10,  5,  5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10,   -2, -1, -1, -1, -1,  -2,  10],
    [5,    -2, -1, -1, -1, -1,  -2,   5],
    [5,    -2, -1, -1, -1, -1,  -2,   5],
    [10,   -2, -1, -1, -1, -1,  -2,  10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10,  5,  5, 10, -20, 100],
] # Focus on Corner

CORNER_ADJ = {
    (0, 0): ((0, 1), (1, 0), (1, 1)),
    (0, 7): ((0, 6), (1, 7), (1, 6)),
    (7, 0): ((7, 1), (6, 0), (6, 1)),
    (7, 7): ((7, 6), (6, 7), (6, 6)),
}

WIN_SCORE = 1_000_000

class SearchCancelled(Exception):
    pass

def dynamic_weights(board):
    w = [row[:] for row in BASE_WEIGHTS]
    g = board.grid
    for (cr, cc), adj in CORNER_ADJ.items():
        if g[cr][cc] != EMPTY:
            for r, c in adj:
                w[r][c] = 6
    return w

def positional_score(board, player, weights):
    s = 0
    g = board.grid
    for r in range(N):
        row, wr = g[r], weights[r]
        for c in range(N):
            v = row[c]
            if v:
                s += wr[c] * v
    return s * player
# BLACK = +1 or WHITE = -1, ie. positive means good for 'player'

def evaluate(board, player):
    opp = -player
    my_mob = board.count_moves(player)
    opp_mob = board.count_moves(opp)
    my_discs = board.count(player)
    opp_discs = board.count(opp)

    if my_mob == 0 and opp_mob == 0:         #Terminal
        diff = my_discs - opp_discs
        if diff > 0:
            return WIN_SCORE + diff
        if diff < 0:
            return -WIN_SCORE + diff
        return 0

    empty = 64 - my_discs - opp_discs
    pos = positional_score(board, player, dynamic_weights(board))
    mobility = 100.0 * (my_mob - opp_mob) / (my_mob + opp_mob) if my_mob + opp_mob else 0.0
    discs = 100.0 * (my_discs - opp_discs) / (my_discs + opp_discs)

    if empty > 44:
        # opening: mobility matters, discs barely
        w_mob, w_disc = 2.0, 0.0
    elif empty > 14:
        #midgame
        w_mob, w_disc = 2.0, 0.4
    else:
        #endgame where disc count dominates
        w_mob, w_disc = 1.0, 4.0
    return pos + w_mob * mobility + w_disc * discs

class Bot:
    def __init__(self, difficulty, player):
        self.difficulty = "Medium"
        self.player = player
        self._stop = threading.Event()
        self.nodes = 0

    def cancel(self):
        # stop any search running in a background thread
        self._stop.set()

    def choose_move(self, board):
        # Board not modified and returns (r, c) or None if no legal moves
        moves = board.valid_moves(self.player)
        if not moves:
            return None
        return self._medium(board, moves)

    # Medium difficulty: One ply positional evaluation
    def _medium(self, board, moves):
        scored = []
        for (r, c), flips in moves.items():
            child = board.copy()
            child.apply_move(r, c, self.player, flips)
            score = positional_score(child, self.player, dynamic_weights(child))
            scored.append((score + random.random() * 0.5, (r, c)))
        return max(scored)[1]

    @staticmethod
    def _ordered(moves):
        # Search corner first/ X-squares last
        return sorted(moves.items(), key = lambda kv: BASE_WEIGHTS[kv[0][0]][kv[0][1]], reverse = True)

    def _negamax(self, board, player, depth, alpha, beta):
        self.nodes += 1
        if self._stop.is_set():
            raise SearchCancelled
        if depth <= 0:
            return evaluate(board, player)
        moves = board.valid_moves(player)
        if not moves:
            if not board.has_moves(-player):
                return evaluate(board, player)      #Game over innit
            return -self._negamax(board, -player, depth - 1, -beta, -alpha)  #pass
        best = - float("inf")
        for (r, c), flips in self._ordered(moves):
            board.apply_move(r, c, player, flips)
            val = -self._negamax(board, -player, depth - 1, -beta, -alpha)
            board.undo_move(r, c, player, flips)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= best:
                break
        return best
