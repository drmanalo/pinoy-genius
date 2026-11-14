"""The rules of Pinoy Genius. No UI code in here, so it is easy to read and test."""
import re
import time
import unicodedata
from dataclasses import dataclass

WAITING, PLAYING, FINISHED = "waiting", "playing", "finished"
ANSWERS = ("Yes", "No", "Maybe")
FILLER_WORDS = {"ba", "po", "ang", "ng", "ay", "yung", "ito", "is", "it", "a", "the"}


def tokens(text):
    """Lowercase, remove accents and punctuation, drop filler words."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9]+", text) if t not in FILLER_WORDS]


def is_correct(guess, word):
    """True if the guess is the word, e.g. 'Aso ba?' matches 'aso'."""
    guess_tokens, word_tokens = tokens(guess), tokens(word)
    if "".join(guess_tokens) == "".join(word_tokens):
        return True
    n = len(word_tokens)
    return any(guess_tokens[i:i + n] == word_tokens for i in range(len(guess_tokens) - n + 1))


@dataclass
class Message:
    kind: str  # "ask", "answer" or "correct"
    text: str


class Game:
    def __init__(self, board, duration=180, clock=time.monotonic):
        self.board = board
        self.duration = duration
        self.clock = clock
        self.state = WAITING
        self.index = 0  # which word is being guessed now
        self.log = []
        self.pending = None  # the question waiting for Yes/No/Maybe
        self.started_at = None
        self.finished_at = None

    @property
    def word(self):
        """The word the Holder sees right now."""
        return self.board[self.index]

    @property
    def guessed(self):
        return self.index

    @property
    def won(self):
        return self.state == FINISHED and self.index == len(self.board)

    def start(self):
        if self.state != WAITING:
            raise RuntimeError("The game already started")
        self.state = PLAYING
        self.started_at = self.clock()

    def elapsed(self):
        if self.started_at is None:
            return 0.0
        end = self.finished_at if self.finished_at is not None else self.clock()
        return min(end - self.started_at, self.duration)

    def remaining(self):
        return max(self.duration - self.elapsed(), 0.0)

    def tick(self):
        """Call this often. Ends the game when the time runs out."""
        if self.state == PLAYING and self.elapsed() >= self.duration:
            self._finish()

    def ask(self, text):
        """The Guesser says something: a category question or a guess."""
        self.tick()
        if self.state != PLAYING:
            raise RuntimeError("The game is not running")
        if self.pending is not None:
            raise RuntimeError("Wait for the Holder to confirm")
        text = text.strip()
        if not text:
            raise ValueError("Ask category or possible answer first")
        if is_correct(text, self.word):
            self.log.append(Message("correct", f"{text} - Tama! ({self.word})"))
            self.index += 1
            if self.index == len(self.board):
                self._finish()
        else:
            self.log.append(Message("ask", text))
            self.pending = text

    def answer(self, reply):
        """The Holder may only say Yes, No or Maybe."""
        self.tick()
        if reply not in ANSWERS:
            raise ValueError(f"The Holder can only say {', '.join(ANSWERS)}")
        if self.state != PLAYING or self.pending is None:
            raise RuntimeError("There is no question to answer")
        self.log.append(Message("answer", reply))
        self.pending = None

    def _finish(self):
        self.state = FINISHED
        self.finished_at = self.clock()
