import pytest

from pinoy_genius.game import Game, FINISHED, PLAYING, is_correct
from pinoy_genius.rooms import GUESSER, HOLDER, RoomManager
from pinoy_genius.words import WORDS, category_of, pick_board

BOARD = ["aso", "halo-halo", "Luneta", "payong", "guro"]


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make_game():
    clock = FakeClock()
    game = Game(list(BOARD), clock=clock)
    game.start()
    return game, clock


def test_is_correct_ignores_case_filler_and_punctuation():
    assert is_correct("Aso ba?", "aso")
    assert is_correct("ASO", "aso")
    assert is_correct("halo halo po", "halo-halo")
    assert is_correct("Is it payong?", "payong")
    assert not is_correct("kaso", "aso")
    assert not is_correct("Hayop ba?", "aso")


def test_holder_can_only_say_yes_no_maybe():
    game, _ = make_game()
    game.ask("Hayop ba?")
    for bad in ("Oo", "maybe", "Hindi ko alam", ""):
        with pytest.raises(ValueError):
            game.answer(bad)
    game.answer("Yes")
    assert game.pending is None


def test_guesser_must_wait_for_answer():
    game, _ = make_game()
    game.ask("Hayop ba?")
    with pytest.raises(RuntimeError):
        game.ask("Pagkain ba?")


def test_correct_guess_advances_and_all_five_wins():
    game, clock = make_game()
    for word in BOARD:
        clock.now += 10
        game.ask(word)
    assert game.state == FINISHED and game.won
    assert game.guessed == 5
    assert game.elapsed() == 50


def test_time_runs_out():
    game, clock = make_game()
    game.ask(BOARD[0])
    clock.now = 310
    game.tick()
    assert game.state == FINISHED and not game.won
    assert game.guessed == 1
    assert game.remaining() == 0
    with pytest.raises(RuntimeError):
        game.ask("halo-halo")


def test_still_playing_before_time_is_up():
    game, clock = make_game()
    clock.now = 179
    game.tick()
    assert game.state == PLAYING


def test_pick_board_is_five_distinct_words():
    board = pick_board()
    assert len(board) == 5 and len(set(board)) == 5
    assert len({category_of(w) for w in board}) == 5


def test_every_word_is_unique_across_categories():
    all_words = [w for ws in WORDS.values() for w in ws]
    assert len(all_words) == len(set(all_words))


def test_rooms_join_and_swap_roles():
    manager = RoomManager()
    room, host = manager.create("Ate")
    _, partner = manager.join(room.code.lower(), "Kuya")
    assert (host.role, partner.role) == (GUESSER, HOLDER)
    with pytest.raises(ValueError):
        manager.join(room.code, "Third")
    with pytest.raises(ValueError):
        manager.join("ZZZZ", "Nobody")
    room.new_round()
    assert (host.role, partner.role) == (HOLDER, GUESSER)
