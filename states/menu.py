import math

import pygame

from constants import (WIDTH, HEIGHT, BG, TEXT, MUTED, BLACK, WHITE, DIFFICULTIES, MODE_PVC, MODE_PVP, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER, BUTTON_DANGER, BUTTON_DANGER_HOVER, PANEL)
from ui import Button, Selector, draw_text, draw_panel
from state_manager import BaseState, StateID

class MenuState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        s = app.settings
        bw, bh = 380, 54
        x = (WIDTH - bw) // 2
        y = 270
        gap = 66
        self.buttons = [
            Button((x, y, bw, bh), "Player vs Computer", lambda: self.start(MODE_PVC), 26, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER),
            Button((x, y + gap, bw, bh), "Play vs Friend (PVP)", lambda: self.start(MODE_PVP), 26, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER)
        ]
        self.difficulty = Selector((x, y + gap * 2, bw, bh), "Difficulty", DIFFICULTIES,
                                   DIFFICULTIES.index(s["difficulty"]),
                                   lambda v: s.__setitem__("difficulty", v))
        colors = ["Black", "White"]
        self.color = Selector((x, y + gap * 3, bw, bh), "Play as", colors, 0 if s["human_color"] == BLACK else 1, lambda v : s.__setitem__("human_color", BLACK if v == "Black" else WHITE))
        self.buttons += [
            Button((x, y + gap * 5, bw, bh), "Quit", app.quit, 26, BUTTON_DANGER, BUTTON_DANGER_HOVER)
        ]
        self.t = 0.0

    def start(self, mode):
        self.app.settings["mode"] = mode
        self.app.manager.change(StateID.PLAYING)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.quit()
            return
        for w in (*self.buttons, self.difficulty, self.color):
            if w.handle_event(event):
                return

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        surf.fill(BG)
        r = self.app.renderer

        panel = pygame.Rect((WIDTH - 460) // 2, 60, 460, HEIGHT - 100)
        draw_panel(surf, panel, PANEL, radius = 22)
        draw_text(surf, "OTHELLO BY VIZLE", 64, TEXT, (WIDTH // 2, 130), anchor = "center", bold = True)
        flip = math.cos(self.t * 2)
        draw_text(surf, "Reversi classic", 18, MUTED, (WIDTH // 2, 245), anchor = "center")
        for w in (*self.buttons, self.difficulty, self.color):
            w.draw(surf)