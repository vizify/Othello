"""Test file """

from engine import Game, player
from constants import BLACK, WHITE, EMPTY

def main():
    game = Game()
    symbols = {EMPTY: ".", BLACK: "B", WHITE: "W"}

    while not game.over:
        b, w = game.score()
        print(f"\n  0 1 2 3 4 5 6 7    [Black (B): {b} | White (W): {w}]")
        for r in range(8):
            row_str = " ".join(symbols.get(game.board.grid[r][c], "?") for c in range(8))
            print(f"{r} {row_str}")

        moves = game.valid_moves()
        print(f"\n{player(game.current)}'s turn. Legal moves: {list(moves.keys())}")

        try:
            user_input = input("Enter row col (e.g. 2 3): ").strip().split()
            if not user_input:
                continue
            r, c = int(user_input[0]), int(user_input[1])
            if not game.play(r, c):
                print(">> Illegal move, try again.")
        except (ValueError, IndexError):
            print(">> Invalid input format. Enter two numbers separated by a space.")

    b, w = game.score()
    print(f"\n=== GAME OVER ===\nFinal Score: Black {b} - {w} White")
    print("Winner:", player(game.winner) if game.winner else "Draw")

if __name__ == "__main__":
    main()