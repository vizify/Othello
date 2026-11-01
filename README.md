# Othello
An unpolished implementation of Othello built with Pygame. Features PVP mode only currently.

## Quick Start

```bash
cd ../Othello
pip install pygame        # or: pip install -r requirements.txt
python main.py
```

Requires Python 3.8+ and Pygame 2.1+.

## Game Features & Controls

| Action | Control / Description |
|---|---|
| **Make Move** | type in the row col integer with space in between to make a move
| **Pass Turn** | Automatic when a player has no legal moves

## Project Structure

```
othello/
├── cli.py                  # Game entry point
├── engine.py                # 8x8 Board & Game rules (legal moves, flips, pass, end)
├── requirements.txt         # Dependencies
├── constants.py
└── README.md
```