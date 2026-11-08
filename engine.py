"""Game Logic"""

try:
    from .constants import EMPTY, BLACK, WHITE, N
except (ImportError, ValueError):
    from constants import EMPTY, BLACK, WHITE, N

DIRECTION = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))  #(Vertical, Horizontal) with (-1,-1) being up-left
COLS = "ABCDEFGH"

def player(p):
    return "Black" if p == BLACK else "White"

def coord(r, c):
    return f"{COLS[c]}{r+1}"

class Board:
    __slots__ = ("grid",)   #Creates a dynamic dict for every instance of the class

    def __init__(self, grid=None):
        if grid is None:
            self.grid = [[EMPTY]*N for _ in range(N)]  #Fills board with no pieces
            m = N // 2
            self.grid[m - 1][m - 1] = WHITE
            self.grid[m][m] = WHITE
            self.grid[m - 1][m] = BLACK
            self.grid[m][m - 1] = BLACK
        else:
            self.grid = grid

    def flips_for(self, r, c, p):
        """returns list of pieces flipped if player plays (r,c); [] if illegal."""
        g = self.grid
        if g[r][c] != EMPTY:
            return []
        opp = -p
        flips = []
        for dr, dc in DIRECTION:
            rr, cc = r + dr, c + dc     #Calculates the adjacent squares in direction dr,dc
            line = []
            while 0 <= rr < N and 0 <= cc < N and g[rr][cc] == opp:
                line.append((rr, cc))
                rr += dr
                cc += dc
            if line and 0 <= rr < N and 0 <= cc < N and g[rr][cc] == p:
                flips.extend(line)
        return flips

    def is_legal(self, r, c, p):
        """legality check"""
        g = self.grid
        if g[r][c] != EMPTY:
            return False
        opp = -p
        for dr,dc in DIRECTION:
            rr, cc = r + dr, c + dc
            seen = False            #At least one opp is along the line
            while 0 <= rr < N and 0 <= cc < N and g[rr][cc] == opp:
                rr += dr
                cc += dc
                seen = True
            if seen and 0 <= rr < N and 0 <= cc < N and g[rr][cc] == p:
                return True
        return False

    def valid_moves(self, p):
        """Computes all legal moves for a player on the current grid"""
        moves = {}
        g = self.grid
        for r in range(N):
            row = g[r]
            for c in range(N):
                if row[c] == EMPTY:
                    f = self.flips_for(r, c, p)
                    if f:
                        moves[(r,c)] = f
        return moves

    def has_move(self, p):
        """checks if the player has any legal move"""
        g = self.grid
        for r in range(N):
            for c in range(N):
                if g[r][c] == EMPTY and self.is_legal(r, c, p):
                    return True
        return False

    def apply_move(self, r, c, p, flips=None):
        """actual flipping the pieces given that the move is legal"""
        if flips is None:
            flips = self.flips_for(r, c, p)
        if not flips:
            raise ValueError(f"Illegal move {coord(r, c)} for {player(p)}")
        self.grid[r][c] = p
        for rr, cc in flips:
            self.grid[rr][cc] = p
        return flips

    def copy(self):
        return Board([row[:] for row in self.grid])

    def count_moves(self, p):
        return len(self.valid_moves(p))

    has_moves = has_move

    def undo_move(self, r, c, p, flips):
        self.grid[r][c] = EMPTY
        opp = -p
        for rr, cc in flips:
            self.grid[rr][cc] = opp

    def count(self, value):
        """counts the number of black and white pieces to determine the winner"""
        return sum(row.count(value) for row in self.grid)

    def empties(self):
        """returns the number of free squares"""
        return self.count(EMPTY)

class Game:
    """turn management like passes, game over, history"""

    def __init__(self):
        self.board = Board()
        self.current = BLACK
        self.history = []       #List of human readable strings for the HUD sidebar later on
        self.last_move = None
        self.over = False
        self.winner = None
        self.status = "Black moves first"  #Also for the HUD sidebar
        self.move_number = 0
        self._moves = None

    def valid_moves(self):
        """Returns legal moves for the current player, with state checks and caching"""
        if self.over:
            return None
        if self._moves is None:
            self._moves = self.board.valid_moves(self.current)
        return self._moves

    def score(self):
        return self.board.count(BLACK), self.board.count(WHITE)

    def play(self, r, c):
        """Executer, basicaly checks validity, execute moves and keep records"""
        if self.over:
            return None
        moves = self.valid_moves()
        if(r,c) not in moves:
            return None
        p = self.current
        flips = self.board.apply_move(r, c, p, moves[(r,c)])
        self.move_number += 1
        self.last_move = (r, c)
        self.history.append(f"{self.move_number:>2}. {player(p)}{coord(r, c)} (+{len(flips)})")
        self._advance_turn()
        return flips

    def _advance_turn(self):
        """Turn switching function"""
        self._moves = None
        nxt = -self.current
        if self.board.has_move(nxt):
            self.current = nxt
            self.status = f"{player(nxt)} to move"
        elif self.board.has_move(self.current):
            # opponent pass; current player moves again
            self.history.append(f"{player(nxt)} passess (no moves)")
            self.status = f"{player(nxt)} has no moves - passes"
        else:
            self._finish()

    def _finish(self):
        self.over = True
        b, w = self.score()
        if b > w:
            self.winner = BLACK
        elif w > b:
            self.winner = WHITE
        else:
            self.winner = None
        reason = "Board full" if self.board.empties() == 0 else "No legal moves"
        result = "Draw" if self.winner is None else f"{player(self.winner)} wins"
        self.status = f"{reason} - {result} {b}-{w}"
        self.history.append(f"Game Over: {result}")