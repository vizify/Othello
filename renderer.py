"""Rendering board and flip animation"""

import math

import pygame
import pygame.gfxdraw

from constants import(
    N, CELL, WIDTH, HEIGHT, BOARD_PIXEL, BOARD_X, BOARD_Y, SIDEBAR_X, SIDEBAR_W, EMPTY, BLACK, BG, FPS, 
    FELT, FELT_LIGHT, FRAME, GRID, TEXT, MUTED, ACCENT, PANEL, PANEL_LIGHT, RED_BAD, BLACK_DISC,
    BLACK_DISC_HI, BLACK_DISC_RIM, WHITE_DISC, WHITE_DISC_HI, WHITE_DISC_RIM, WHITE, PLACE_DURATION, FLIP_DURATION
)
from engine import COLS
from ui import draw_text, draw_shadow, draw_panel, fit_text

PIECE_R = int(CELL * 0.40)

def ease_out_back(t):
    c1 = 1.7
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
    
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

class BoardRenderer:
    def __init__(self, board=None):
        self.board_surface = self._build_board()
        self._piece_shadow_cache = {}
    """Static Board"""
    def _build_board(self):
        pad = 18
        surf = pygame.Surface((BOARD_PIXEL + pad * 2, BOARD_PIXEL + pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(surf, FRAME, surf.get_rect(), border_radius=18)
        felt = pygame.Surface((BOARD_PIXEL, BOARD_PIXEL), pygame.SRCALPHA)
        #subtle radial light in the cneter of the felt
        glow = pygame.Surface((BOARD_PIXEL, BOARD_PIXEL), pygame.SRCALPHA)
        for i in range(24, 0, -1):
            rad = int(BOARD_PIXEL * 0.75 * i / 24)
            pygame.draw.circle(glow, (*FELT_LIGHT, 10), (BOARD_PIXEL // 2, BOARD_PIXEL // 2), rad)
        felt.blit(glow, (0, 0))
        for i in range(N + 1):
            p = i * CELL
            w = 3 if i in (0, N) else 2
            pygame.draw.line(felt, GRID, (p, 0), (p, BOARD_PIXEL), w)
            pygame.draw.line(felt, GRID, (0, p), (BOARD_PIXEL, p), w)
        for r, c in ((2, 2), (2, 6), (6, 2), (6, 6)):
            pygame.gfxdraw.aacircle(felt, c * CELL, r * CELL, 5, GRID)
            pygame.gfxdraw.filled_circle(felt, c * CELL, r * CELL, 5, GRID)
        surf.blit(felt, (pad, pad))
        self._pad = pad
        return surf

    def cell_at(self, pos):
        x, y = pos[0] - BOARD_X, pos[1] - BOARD_Y
        if 0 <= x < BOARD_PIXEL and 0 <= y < BOARD_PIXEL:
            return int(y // CELL), int(x // CELL)
        return None

    @staticmethod
    def cell_center(r, c):
        return BOARD_X + c * CELL + CELL // 2, BOARD_Y +r * CELL + CELL // 2

    # Pieces
    def _shadow(self, rx, ry):
        key = (rx, ry)
        if key not in self._piece_shadow_cache:
            s = pygame.Surface((rx * 2 + 12, ry * 2 + 12), pygame.SRCALPHA)
            for i, a in enumerate((25, 35, 50)):
                pygame.draw.ellipse(s, (0, 0, 0, a), (i * 2, i * 2, rx * 2 + 12 - i * 4, ry * 2 + 12 - i * 4))
            self._piece_shadow_cache[key] = s
        return self._piece_shadow_cache[key]

    def draw_piece(self, surf, cx, cy, color, sx=1.0, scale=1.0, alpha=255, lift=0.0):
        ry = max(1, int(PIECE_R * scale))
        rx = max(1, int(PIECE_R * scale * abs(sx)))
        if alpha == 255:
            sh = self._shadow(rx, ry)
            off = 3 + int(lift * 10)
            surf.blit(sh, (cx - rx - 6 + off, cy - ry - 6 + off + 2))

        cy -= int (lift * 8)
        if color == BLACK:
            base, hi, rim = BLACK_DISC, BLACK_DISC_HI, BLACK_DISC_RIM
        else:
            base, hi, rim = WHITE_DISC, WHITE_DISC_HI, WHITE_DISC_RIM

        target = surf
        if alpha != 255:
            target = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
            ox, oy = cx - rx - 2, cy - ry - 2

        pygame.gfxdraw.filled_ellipse(target, cx, cy, rx, ry, base)
        pygame.gfxdraw.aaellipse(target, cx, cy, rx, ry, rim)
        irx, iry = max(1, rx - 3), max(1, ry - 3)
        pygame.gfxdraw.filled_ellipse(target, cx, cy, irx, iry, base)
        pygame.gfxdraw.aaellipse(target, cx, cy, irx, iry, base)
        # glossy highlight gradient toward top-left
        for i in range(1, 5):
            t = i / 5
            hrx, hry = max(1, int(irx * (1 - t * 0.5))), max(1, int(iry * (1 - t * 0.5)))
            hx = cx - int(irx * 0.3 * t)
            hy = cy - int(iry * 0.3 * t)
            pygame.gfxdraw.filled_ellipse(target, hx, hy, hrx, hry, lerp_color(base, hi, t * 0.5))

        if alpha < 255:
            target.set_alpha(alpha)
            surf.blit(target, (ox, oy))

    # full board
    def draw(self, surf, game, hints=None, hover=None, anim=None, now = 0.0, hover_color=None):
        pad = self._pad
        brect = pygame.Rect(BOARD_X - pad, BOARD_Y - pad, BOARD_PIXEL + pad * 2, BOARD_PIXEL + pad * 2)
        draw_shadow(surf, brect, radius=18, offset=(4, 6), spread=16, alpha=160)
        surf.blit(self.board_surface, brect.topleft)

        #coordinates    
        for i in range(N):
            draw_text(surf, COLS[i], 20, (150, 200, 160), (BOARD_X + i * CELL + CELL // 2, BOARD_Y - pad // 2 - 1), anchor="center", bold=True)
            draw_text(surf, str(i + 1), 20, (150, 200, 160), (BOARD_X - pad // 2 - 1, BOARD_Y + i * CELL + CELL // 2), anchor="center", bold=True)

        #hints (valid moves)
        if hints:
            hint_s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            pygame.gfxdraw.filled_circle(hint_s, CELL // 2, CELL // 2, 8, (255, 255, 255, 100))
            pygame.gfxdraw.aacircle(hint_s, CELL // 2, CELL // 2, 9, (255, 255, 255, 150))
            for (r, c) in hints:
                if hover == (r, c):
                    hl = pygame.Surface((CELL - 4, CELL - 4), pygame.SRCALPHA)
                    hl.fill((255, 255, 255, 20))
                    surf.blit(hl, (BOARD_X + c * CELL + 2, BOARD_Y + r * CELL + 2))
                    cx, cy = self.cell_center(r, c)
                    self.draw_piece(surf, cx, cy, hover_color, alpha = 100)
                else:
                    surf.blit(hint_s, (BOARD_X + c * CELL, BOARD_Y + r * CELL))

        #pieces animation
        placed, flip_map, elapsed = None, {}, 0.0
        if anim:
            placed = anim["placed"]
            flip_map = anim["flips"]
            elapsed = now - anim["start"]
        g = game.board.grid
        for r in range(N):
            for c in range(N):
                v = g[r][c]
                if v == EMPTY:
                    continue
                cx, cy = self.cell_center(r, c)
                if (r, c) == placed and elapsed < PLACE_DURATION:
                    t = max(0.0, elapsed / PLACE_DURATION)
                    self.draw_piece(surf, cx, cy, v, scale=max(0.05, ease_out_back(t)))
                elif (r, c) in flip_map:
                    t = (elapsed - flip_map[(r, c)]) / FLIP_DURATION
                    t = min(1.0, max(0.0, t))
                    color = -v if t < 0.5 else v
                    sx = math.cos(t * math.pi)
                    lift = math.sin(t * math.pi)
                    self.draw_piece(surf, cx, cy, color, sx=sx, scale=1 + 0.10 * lift, lift=lift)
                else:
                    self.draw_piece(surf, cx, cy, v)

        # Last move maker
        if game.last_move and not (anim and elapsed < PLACE_DURATION):
            r, c = game.last_move
            cx, cy = self.cell_center(r, c)
            pygame.gfxdraw.filled_circle(surf, cx, cy, 5, RED_BAD)
            pygame.gfxdraw.aacircle(surf, cx, cy, 5, RED_BAD)

    # sidebar
    def draw_sidebar(self, surf, game, info):
        """info: dict with mode_text, labels {BLACK: str, WHITE: str}, turn_next, thinking"""
        x, w = SIDEBAR_X, SIDEBAR_W
        panel = pygame.Rect(x, 22, w, HEIGHT - 44)
        draw_panel(surf, panel, PANEL, radius = 15)

        y = panel.y + 18
        draw_text(surf, "OTHELLO BY VIZLE", 30, TEXT, (x + 20, y), bold = True)
        y += 40
        draw_text(surf, info ["mode_text"], 15, MUTED, (x + 20, y))
        y += 35

        b, wh = game.score()
        for player, count in ((BLACK, b), (-BLACK, wh)):
            card = pygame.Rect(x + 15, y, w - 32, 62)
            active = (not game.over) and game.current == player
            pygame.draw.rect(surf, PANEL_LIGHT, card, border_radius=12)
            if active:
                pygame.draw.rect(surf, ACCENT, card, 3, border_radius=12)
            self.draw_piece(surf, card.x + 34, card.centery, player, scale=0.6)
            name = "Black" if player == BLACK else "White"
            draw_text(surf, name, 21, TEXT, (card.x + 64, card.y + 10), bold=True)
            draw_text(surf, info["labels"][player], 15, MUTED, (card.x + 64, card.y + 36))
            draw_text(surf, str(count), 34, TEXT, (card.right - 16, card.centery), anchor="midright", bold=True)
            y += 72

        #turn / status
        y += 4
        turn_color = ACCENT if not game.over else TEXT
        turn_next = info.get("turn_next") or info.get("turn_text", "")
        if info.get("thinking"):
            turn_next += "." * (int(pygame.time.get_ticks() / 333) % 4)
        draw_text(surf, turn_next, 20, turn_color, (x + 20, y), bold=True)
        y += 30
        status = fit_text(game.status, 15, w - 40)
        draw_text(surf, status, 15, MUTED, (x + 20, y))
        y += 32

        #move history
        draw_text(surf, "MOVE HISTORY", 14, MUTED, (x + 20, y), bold = True)
        y += 22
        hist_rect = pygame.Rect(x + 16, y, w - 32, info["history_bottom"] - y)
        pygame.draw.rect(surf, (28, 32, 40), hist_rect, border_radius=10)
        line_h = 20
        max_lines = max(0, (hist_rect.h - 12) // line_h)
        lines = game.history[-max_lines:] if max_lines else []
        ly = hist_rect.y + 8
        for i, line in enumerate(lines):
            is_last = i == len(lines) - 1
            col = TEXT if is_last else MUTED
            if "pass" in line or "Game over" in line:
                col = ACCENT
            draw_text(surf, fit_text(line, 15, hist_rect.w - 20), 15, col, (hist_rect.x + 10, ly))
            ly += line_h


# if __name__ == "__main__":
#     from engine import Game

#     pygame.init()
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     pygame.display.set_caption("Renderer Test")
#     clock = pygame.time.Clock()

#     game = Game()
#     renderer = BoardRenderer(game.board)

#     running = True
#     while running:
#         hover_cell = renderer.cell_at(pygame.mouse.get_pos())
#         valid_moves = game.valid_moves()

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 if hover_cell and hover_cell in valid_moves:
#                     game.play(*hover_cell)

#         # Prepare sidebar info dictionary
#         info = {
#             "mode_text": "PVP Test Mode",
#             "labels": {BLACK: "Player 1", WHITE: "Player 2"},
#             "turn_next": "Black's Turn" if game.current == BLACK else "White's Turn",
#             "history_bottom": HEIGHT - 30,
#             "thinking": False,
#         }

#         # Draw frame
#         screen.fill(BG)
#         renderer.draw(
#             screen,
#             game,
#             hints=list(valid_moves.keys()),
#             hover=hover_cell,
#             hover_color=game.current,
#         )
#         renderer.draw_sidebar(screen, game, info)

#         pygame.display.flip()
#         clock.tick(FPS)

#     pygame.quit()