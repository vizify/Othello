import pygame

from constants import WIDTH, HEIGHT, FPS, TITLE, BLACK, MODE_PVC
from renderer import BoardRenderer
from state_manager import StateManager, StateID
from states.menu import MenuState
from states.playing import Playing
from states.game_over import GameOver

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True

        self.settings = {"mode": MODE_PVC, "difficulty": "Medium", "human_color" : BLACK}
        self.renderer = BoardRenderer()

        self.manager = StateManager()
        self.manager.register(StateID.MENU, MenuState(self))
        self.manager.register(StateID.PLAYING, Playing(self))
        self.manager.register(StateID.GAME_OVER, GameOver(self))
        self.manager.change(StateID.MENU)
        pygame.key.stop_text_input()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.manager.current.handle_event(event)
            if not self.running:
                break
            self.manager.current.update(dt)
            self.manager.current.draw(self.screen)
            pygame.display.flip()
        if self.manager.current is not None:
            self.manager.current.exit()
        pygame.quit()