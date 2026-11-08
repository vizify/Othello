import pygame

from constants import(WIDTH, HEIGHT, TEXT, MUTED, ACCENT, GREEN_OK, RED_BAD, PANEL, MODE_PVC, BLACK, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER)
from engine import player
from state_manager import BaseState, StateID
from ui import Button, TextInput, draw_text, draw_panel

class GameOver(BaseState):
    PANEL_W, PANEL_H = 520, 400
    def __init__(self, app):
        super().__init__(app)
        self.panel = pygame.Rect((WIDTH - self.PANEL_W) // 2, (HEIGHT - self.PANEL_H) // 2, self.PANEL_W, self.PANEL_H)
        p = self.panel
        self.input = TextInput((p.x + 60, p.y + 220, p.w - 120, 45))
        bw, gap = 140, 15
        bx = p.centerx - (bw * 3 + gap * 2) // 2
        by = p.bottom - 80
        self.save_btn = Button((bx, by, bw, 50), "Save", self.save, 25, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER)
        self.again_btn = Button((bx + bw + gap, by, bw, 50), "Play Again", lambda: app.manager.change(StateID.MENU), 20)
        self.menu_btn = Button((bx + 2 * (bw + gap), by, bw, 50), "Menu", lambda: app.manager.change(StateID.MENU), 25)

    def enter(self, screen = None, **kwargs):
        self.screen = screen
        game = screen.game
        s = self.app.settings
        b, w = game.score()
        self.score_line = f"Black {b} - {w} White"
        self.input.text = ""
        self.input.active = True
        self.message = ""

        if screen.mode == MODE_PVC:
            human = screen.human_color
            hs, os_ = (b, w) if human == BLACK else (w, b)
            if game.winner is None:
                self.headline, self.color, self.result = "Draw!", ACCENT, "Draw"
            elif game.winner == human:
                self.headline, self.color, self.result = "You Win!", GREEN_OK, "Win"
            else:
                self.headline, self.color, self.result = "You Lose!", RED_BAD, "Loss"

        else:
            if game.winner is None:
                self.headline, self.color, self.record = "Draw!", ACCENT, None
            else:
                self.headline = f"{player(game.winner)} Wins!"
                self.color = GREEN_OK
                ws, ls = (b, w) if game.winner == BLACK else (w, b)
                self.result = "Win"

    def exit(self):
        pygame.key.stop_text_input()

    def save(self):
        pass        #Leaderboard not implemented yet

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.manager.change(StateID.MENU)
            return
        for b in (self.again_btn, self.menu_btn):
            if b.handle_event(event):
                return

    def draw(self, surf):
        self.screen.draw(surf)
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        surf.blit(dim, (0, 0))

        p = self.panel
        draw_panel(surf, p, PANEL, radius=20, border=self.color)
        draw_text(surf, "GAME OVER", 20, MUTED, (p.centerx, p.y + 35), anchor="center", bold=True)
        draw_text(surf, self.headline, 50, self.color, (p.centerx, p.y + 90), anchor="center", bold=True)
        draw_text(surf, self.score_line, 30, TEXT, (p.centerx, p.y + 150), anchor="center")
        for b in (self.again_btn, self.menu_btn):
            b.draw(surf)
