import threading
import time

import pygame

from ai import Bot
from constants import (BG, MODE_PVC, BLACK, WHITE, SIDEBAR_X, SIDEBAR_W, HEIGHT, BOT_DELAY, PLACE_DURATION, FLIP_DURATION, FLIP_STAGGER, GAMEOVER_DELAY, BUTTON_DANGER, BUTTON_DANGER_HOVER)
from engine import Game, player
from state_manager import BaseState, StateID
from ui import Button

class Playing(BaseState):
    def __init__(self, app):
        super().__init__(app)
        bx, bw = SIDEBAR_X + 15, SIDEBAR_W - 30
        rw = 95
        self.restart_button = Button((bx, HEIGHT - 90, rw, 50), "Restart", self.restart, 20)
        self.menu_button = Button((bx + rw + 10, HEIGHT - 90, bw - rw - 10, 50), "Return to Menu", self.to_menu, 20, BUTTON_DANGER, BUTTON_DANGER_HOVER)
        self.history_bottom = HEIGHT - 110
        self.game = None
        self.bot = None

    def enter(self, **kwargs):
        s = self.app.settings
        self.mode = s["mode"]
        self.difficulty = "Medium"
        self.human_color = s["human_color"]
        self.game = Game()
        self.bot = Bot(self.difficulty, -self.human_color) if self.mode == MODE_PVC else None
        self.bot_job = None
        self.anim = None
        self.hover = None
        self.game_over_at = None

    def exit(self):
        self._cancel_bot()

    def _cancel_bot(self):
        if self.bot:
            self.bot.cancel()
        self.bot_job = None

    def restart(self):
        self._cancel_bot()
        self.enter()

    def to_menu(self):
        self._cancel_bot()
        self.app.manager.change(StateID.MENU)

    def is_bot_turn(self):
        return self.bot is not None and not self.game.over and self.game.current == self.bot.player

    def is_human_turn(self):
        return not self.game.over and not self.is_bot_turn()

    def make_move(self, r, c):
        player = self.game.current
        flips = self.game.play(r, c)
        if flips is None:
            return False
        delays = {}
        for fr, fc in flips:
            dist = max(abs(fr - r), abs(fc - c))
            delays[(fr, fc)] = PLACE_DURATION * 0.6 + (dist - 1) * FLIP_STAGGER
        duration = max(PLACE_DURATION, max(delays.values()) + FLIP_DURATION)
        self.anim = {"placed" : (r, c), "player": player, "flips" : delays, "start": time.perf_counter(), "duration": duration}

        return True

    def _start_bot_job(self, now):
        job = {"done": False, "move" : None, "start": now}
        board = self.game.board.copy()
        bot = self.bot

        def worker():
            try:
                job["move"] = bot.choose_move(board)
            finally:
                job["done"] = True

        threading.Thread(target=worker, daemon=True).start()
        self.bot_job = job

    start_bot_job = _start_bot_job

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.to_menu()
            return
        if self.restart_button.handle_event(event) or self.menu_button.handle_event(event):
            return
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.app.renderer.cell_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.anim or not self.is_human_turn():
                return
            cell = self.app.renderer.cell_at(event.pos)
            if cell and cell in self.game.valid_moves():
                self.make_move(*cell)

    def update(self, dt):
        now = time.perf_counter()
        if self.anim:
            if now - self.anim["start"] >= self.anim["duration"]:
                self.anim = None
            else:
                return
        if self.game.over:
            if self.game_over_at is None:
                self.game_over_at = now
            elif now - self.game_over_at >= GAMEOVER_DELAY:
                self.app.manager.change(StateID.GAME_OVER, screen=self)
            return
        if self.is_bot_turn():
            if self.bot_job is None:
                self._start_bot_job(now)
            elif self.bot_job["done"] and now - self.bot_job["start"] >= BOT_DELAY:
                move = self.bot_job["move"]
                self.bot_job = None
                if move is not None:
                    self.make_move(*move)

    def draw(self, surf):
        surf.fill(BG)
        g = self.game
        show_hints = self.is_human_turn() and not self.anim
        hints = g.valid_moves() if show_hints else None
        self.app.renderer.draw(surf, g, hints=hints, hover=self.hover, anim=self.anim, now=time.perf_counter(), hover_color=g.current)

        if self.mode == MODE_PVC:
            labels = {self.human_color : "You", -self.human_color: f"Computer ({self.difficulty})"}
            mode_text = f"Player vs Computer - {self.difficulty}"
        else:
            labels = {BLACK : "Player 1", WHITE : "Player 2"}
            mode_text = "Player vs Player"

        thinking = False
        if g.over:
            turn_text = "Game over"
        elif self.is_bot_turn():
            turn_text = "Computer is thinking"
            thinking = True
        elif self.mode == MODE_PVC:
            turn_text = f"Your turn ({player(g.current)})"
        else:
            turn_text = f"{player(g.current)}'s turn"

        self.app.renderer.draw_sidebar(surf, g, {"mode_text" : mode_text, "labels" : labels, "turn_text" : turn_text, "thinking" : thinking, "history_bottom" : self.history_bottom})
        self.restart_button.draw(surf)
        self.menu_button.draw(surf) 