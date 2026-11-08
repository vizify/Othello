import pygame
from constants import WIDTH, HEIGHT, FPS, MODE_PVC, BLACK
from renderer import BoardRenderer
from state_manager import StateManager, StateID
from states.menu import MenuState

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
menu = MenuState(app)

while app.running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app.running = False
        menu.handle_event(event)
    menu.update(dt)
    menu.draw(screen)
    pygame.display.flip()

pygame.quit()