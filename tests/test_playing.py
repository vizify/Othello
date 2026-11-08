import pygame
from constants import WIDTH, HEIGHT, FPS, MODE_PVC, BLACK
from renderer import BoardRenderer
from state_manager import StateManager, StateID
from states.playing import Playing
from states.game_over import GameOver
from states.menu import MenuState

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Playing State")
clock = pygame.time.Clock()

class DummyApp:
    def __init__(self):
        self.settings = {"mode": MODE_PVC, "difficulty": "Medium", "human_color": BLACK}
        self.renderer = BoardRenderer()
        self.manager = StateManager()
        self.running = True

    def quit(self):
        self.running = False

app = DummyApp()

# Register states
playing_state = Playing(app)
menu_state = MenuState(app)
game_over_state = GameOver(app)

app.manager.register(StateID.PLAYING, playing_state)
app.manager.register(StateID.MENU, menu_state)
app.manager.register(StateID.GAME_OVER, game_over_state)

# Start directly in PLAYING state (transitioning from MENU)
app.manager.current_id = StateID.MENU
app.manager.change(StateID.PLAYING)

while app.running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app.running = False
        app.manager.current.handle_event(event)

    app.manager.current.update(dt)
    app.manager.current.draw(screen)
    pygame.display.flip()

pygame.quit()
