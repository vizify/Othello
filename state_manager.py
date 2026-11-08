from enum import Enum, auto

class StateID(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    LEADERBOARD = auto()

TRANSITIONS = {
    None : {StateID.MENU},
    StateID.MENU : {StateID.PLAYING},
    StateID.PLAYING : {StateID.MENU, StateID.GAME_OVER, StateID.PLAYING},
    StateID.GAME_OVER : {StateID.MENU, StateID.PLAYING}
}

class BaseState:
    def __init__(self, app):
        self.app = app

    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass

class StateManager:
    def __init__(self):
        self.states = {}
        self.current_id = None
        self.current = None

    def register(self, state_id, state):
        self.states[state_id] = state

    def change(self, state_id, **kwargs):
        if state_id not in TRANSITIONS[self.current_id]:
            raise RuntimeError(f"Illegal state transition {self.current_id} -> {state_id}")
        if self.current is not None:
            self.current.exit()
        self.current_id = state_id
        self.current = self.states[state_id]
        self.current.enter(**kwargs)