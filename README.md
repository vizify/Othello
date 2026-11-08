# Oh~ thello (Othello by Vizle)

A sleek, modern Othello (Reversi) desktop game built in Python using **Pygame**. Features an animated felt board, intuitive mouse controls, real-time move validation, and AI opponents.

---

## Features

- **Game Modes:**
  - **Player vs Computer (PVC):** Play against an AI bot with positional evaluation.
  - **Player vs Player (PVP):** Classic 2-player local pass-and-play.
- **Visuals & Polish:**
  - Styled felt board with radial illumination and grid coordinates.
  - Realistic 3D disc rendering with glossy highlights and drop shadows.
  - Smooth piece-placement bounce and staggered flip animations.
  - Valid-move hint markers and disc hover previews.
- **Sidebar HUD:**
  - Real-time score cards for Black and White.
  - Active turn indicator with animated thinking states.
  - Scrollable move history log.
- **State System:**
  - Start menu with customizable difficulty and color picker (Play as Black or White).
  - In-game restart and return-to-menu buttons.
  - Game Over modal with score summary and rematch options.

---

## Quick Start

### Prerequisites
- Python 3.8+
- [Pygame](https://www.pygame.org/)

### Installation

```bash
git clone https://github.com/your-username/Othello.git
cd Othello
pip install -r requirements.txt
```

### Run the Game

```bash
python app.py
```
*(or `python main.py`)*

---

## Controls

| Action | Control |
|---|---|
| **Place Disc** | Left Click on any highlighted legal move |
| **Move Preview** | Hover mouse over valid board squares |
| **Quick Return to Menu** | `Esc` key or sidebar button |
| **Restart Match** | Sidebar "Restart" button |

---

## Building Standalone Executable (Windows)

To bundle the game into a standalone `.exe` without requiring Python to be installed:

```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console app.py
```

The compiled standalone executable will be generated as `app.exe`.

---

## Project Structure

```
Othello/
├── app.py              # Main application loop and state orchestrator
├── main.py             # Alternative bootstrap entry point
├── engine.py           # Core Othello rules, board representation, and flip logic
├── ai.py               # Bot logic and positional heuristics
├── renderer.py         # Board surfaces, pieces, coordinates, and flip animation engine
├── state_manager.py    # State machine and transition management
├── ui.py               # UI components (Buttons, Selectors, Panels, Shadows, Text)
├── constants.py        # Color palettes, timing configs, and dimensions
├── states/
│   ├── menu.py         # Main menu state
│   ├── playing.py      # Active gameplay state
│   └── game_over.py    # Game over modal overlay
├── requirements.txt    # Project dependencies
└── README.md
```
