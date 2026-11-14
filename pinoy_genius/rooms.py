"""Rooms: how two players find each other with a 4-letter code."""
import random
import secrets
from dataclasses import dataclass

from .game import Game
from .words import pick_board

GUESSER, HOLDER = "Guesser", "Holder"
CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # no I or O, they look like 1 and 0


@dataclass
class Player:
    id: str
    name: str
    role: str


class Room:
    def __init__(self, code):
        self.code = code
        self.players = []
        self.game = Game(pick_board())

    def join(self, name):
        if len(self.players) >= 2:
            raise ValueError("The room is full")
        role = GUESSER if not self.players else HOLDER
        player = Player(secrets.token_urlsafe(8), name.strip() or "Player", role)
        self.players.append(player)
        return player

    def player(self, player_id):
        return next((p for p in self.players if p.id == player_id), None)

    def partner_of(self, player):
        return next((p for p in self.players if p is not player), None)

    @property
    def ready(self):
        return len(self.players) == 2

    def new_round(self):
        """Fresh board, and the partners swap roles."""
        for p in self.players:
            p.role = HOLDER if p.role == GUESSER else GUESSER
        self.game = Game(pick_board())


class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create(self, name):
        code = "".join(random.choices(CODE_LETTERS, k=4))
        while code in self.rooms:
            code = "".join(random.choices(CODE_LETTERS, k=4))
        room = self.rooms[code] = Room(code)
        return room, room.join(name)

    def join(self, code, name):
        room = self.rooms.get(code.strip().upper())
        if room is None:
            raise ValueError("No room with that code")
        return room, room.join(name)
