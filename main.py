import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from app import App
except ImportError:
    from Othello.app import App

def main():
    App().run()

if __name__ == "__main__":
    main()