import pygame

from constants import(TEXT, MUTED, BUTTON, BUTTON_HOVER, PANEL_LIGHT, ACCENT)

_font_cache = {}
_shadow_cache = {}
FONT_NAMES = "segoeui,helveticaneue,helvetica,dejavusans,arial"

def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(FONT_NAMES, size, bold=bold)
    return _font_cache[key]

def draw_text(surf, text, size, color, pos, anchor="topleft", bold=False):
    img = font(size, bold).render(str(text), True, color)
    rect = img.get_rect(**{anchor: pos})
    surf.blit(img, rect)
    return rect

def fit_text(text, size, max_w, bold=False):
    """Truncate text with an ellipsis so it fits within max_w pixels"""
    f = font(size, bold)
    if f.size(text)[0] <= max_w:
        return text
    while text and f.size(text + "…")[0] > max_w:
        text = text[:-1]
    return text + "…"

def soft_shadow(size, radius=12, spread=10, alpha=120):
    """Cached blurred-looking shadow surface, aka layered translucent rects"""
    key = (size, radius, spread, alpha)
    if key not in _shadow_cache:
        w, h = size
        surf = pygame.Surface((w + spread * 2, h + spread * 2), pygame.SRCALPHA)
        step = max(1, alpha // spread)
        for i in range(spread):
            pygame.draw.rect(surf, (0, 0, 0, step),
                             (i, i, w + (spread - i) * 2, h + (spread - i) * 2),
                             border_radius=radius + spread - i)
        _shadow_cache[key] = surf
    return _shadow_cache[key]

def draw_shadow(surf, rect, radius=12, offset=(4, 6), spread=10, alpha=120):
    sh = soft_shadow((rect.w, rect.h), radius, spread, alpha)
    surf.blit(sh, (rect.x - spread + offset[0], rect.y - spread + offset[1]))

def draw_panel(surf, rect, color=PANEL_LIGHT, radius=14, shadow=True, border=None):
    if shadow:
        draw_shadow(surf, rect, radius)
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border[0], rect, width=border[1], border_radius=radius)

class Button:
    def __init__(self, rect, text, callback=None, size=24, color=BUTTON,
                 hover_color=BUTTON_HOVER, text_color=TEXT, radius=10):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.enabled = True
        self.visible = True

    def hovered(self):
        """Return True if mouse is over button"""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        """Call callback if button is clicked"""
        if (self.enabled and self.visible and self.rect.collidepoint(pygame.mouse.get_pos()) and
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            if self.callback:
                self.callback()
            return True
        return False

    def draw(self, surf):
        """Draw button on surface"""
        if not self.visible:
            return
        hov = self.hovered()
        rect = self.rect
        draw_shadow(surf, rect, self.radius, offset=(2,4) if not hov else (3,7), spread=6, alpha=100)
        color = self.hover_color if hov else self.color
        if not self.enabled:
            color = tuple(int(c * 0.6) for c in self.color)
        pygame.draw.rect(surf, color, rect, border_radius=self.radius)
        tc = self.text_color if self.enabled else MUTE
        draw_text(surf, self.text, self.size, tc, rect.center, anchor="center", bold=True)

class Selector:
    """'<  Option  >' widget cycling through a list of options."""
    def __init__(self, rect, options, label, index=0, on_change=None, size=24):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.label = label
        self.index = index
        self.on_change = on_change
        self.size = size
        aw = self.rect.h
        self.left = Button((self.rect.x, self.rect.y, aw, aw), "<", lambda: self.step(-1), size)
        self.right = Button((self.rect.right - aw, self.rect.y, aw, aw), ">", lambda: self.step(1), size)
        self.center = pygame.Rect(self.rect.x + aw + 8, self.rect.y, self.rect.w - 2 * aw - 16, self.rect.h)

    @property
    def value(self):
        return self.options[self.index]

    def step(self, d):
        self.index = (self.index + d) % len(self.options)
        if self.on_change:
            self.on_change(self.value)

    def handle_event(self, event):
        if self.left.handle_event(event) or self.right.handle_event(event):
            return True
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.center.collidepoint(event.pos)):
            self.step(1)
            return True
        return False

    def draw(self, surf):
        self.left.draw(surf)
        self.right.draw(surf)
        hover = self.center.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surf, BUTTON_HOVER if hover else BUTTON, self.center, border_radius=8)
        draw_text(surf, f"{self.label}: ", self.size, MUTED, (self.center.centerx, self.center.centery), anchor="midright")
        draw_text(surf, self.value, self.size, ACCENT, (self.center.centerx, self.center.centery), anchor="midleft", bold=True)

class TextInput:
    def __init__(self, rect, max_len=16, placeholder="Your Name", size=26):
        self.rect = pygame.Rect(rect)
        self.max_len = max_len
        self.placeholder = placeholder
        self.size = size
        self.text = ""
        self.active = True
        self._blink = 0.0

    def handle_event(self, event):
        """Returns 'submit' when Enter is pressed"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return None
        if event.type == pygame.TEXTINPUT:
            for ch in event.text:
                if ch.isprintable() and len(self.text) < self.max_len:
                    self.text += ch
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "submit"
        return None

    def update(self, dt):
        self._blink = (self._blink + dt) % 1.0

    def draw(self, surf):
        pygame.draw.rect(surf, (24, 28, 35), self.rect, border_radius=8)
        pygame.draw.rect(surf, ACCENT if self.active else BUTTON_HOVER, self.rect, width=2, border_radius=8)
        x, cy = self.rect.x + 14, self.rect.centery
        if self.text:
            r = draw_text(surf, self.text, self.size, TEXT, (x, cy), anchor="midleft")
            cursor_x = r.right + 2
        else:
            draw_text(surf, self.placeholder, self.size, MUTED, (x, cy), anchor="midleft")
            cursor_x = x
        if self.active and self._blink < 0.5:
            pygame.draw.line(surf, TEXT, (cursor_x, cy - self.size // 2), (cursor_x, cy + self.size // 2), 2)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    pygame.display.set_caption("UI Test")
    clock = pygame.time.Clock()

    text_input = TextInput((150, 80, 300, 45), placeholder="Enter your name...")
    sel = Selector((150, 150, 300, 45), ["Easy", "Medium", "Hard"], label="Difficulty")
    btn = Button((200, 220, 200, 50), "Submit", callback=lambda: print(f"Submitted name: {text_input.text}, difficulty: {sel.value}"))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds passed for cursor blinking

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            btn.handle_event(event)
            sel.handle_event(event)
            result = text_input.handle_event(event)
            if result == "submit":
                print(f"Enter pressed! Name: {text_input.text}")

        text_input.update(dt)

        screen.fill((22, 26, 32))
        draw_panel(screen, pygame.Rect(100, 40, 400, 260))
        text_input.draw(screen)
        sel.draw(screen)
        btn.draw(screen)

        pygame.display.flip()

    pygame.quit()