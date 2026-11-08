import pygame
from constants import WIDTH, HEIGHT, FPS, MODE_PVC, BLACK, WHITE
from engine import Game
from renderer import BoardRenderer
from state_manager import StateManager, StateID
from states.game_over import GameOver

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Game Over Screen")
clock = pygame.time.Clock()

class DummyApp:
    def __init__(self):
        self.settings = {"mode": MODE_PVC, "difficulty": "Medium", "human_color": BLACK}
        self.renderer = BoardRenderer()
        self.manager = StateManager()
        self.running = True

class DummyPlayingState:
    """Mocks the active game state passed into enter(screen=...)."""
    def __init__(self, app):
        self.app = app
        self.mode = MODE_PVC
        self.human_color = BLACK
        self.game = Game()
        # Simulate an ended game
        self.game.over = True
        self.game.winner = BLACK

    def draw(self, surf):
        surf.fill((30, 30, 30))
        self.app.renderer.draw(surf, self.game)

app = DummyApp()
game_over = GameOver(app)
mock_playing_state = DummyPlayingState(app)

# Initialize GameOver state with mock game
game_over.enter(screen=mock_playing_state)

while app.running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app.running = False
        game_over.handle_event(event)

    game_over.update(dt)
    game_over.draw(screen)
    pygame.display.flip()

pygame.quit()