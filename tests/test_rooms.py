import random

import pytest

from pinoy_genius.game import WAITING
from pinoy_genius.rooms import CODE_LETTERS, GUESSER, HOLDER, Room, RoomManager


def make_full_room():
    manager = RoomManager()
    room, host = manager.create("Ate")
    _, partner = manager.join(room.code, "Bunso")
    return manager, room, host, partner


def test_create_makes_a_four_letter_code_and_a_guesser_host():
    manager = RoomManager()
    room, host = manager.create("Kuya")
    assert len(room.code) == 4
    assert all(c in CODE_LETTERS for c in room.code)
    assert manager.rooms[room.code] is room
    assert (host.name, host.role) == ("Kuya", GUESSER)
    assert not room.ready


def test_codes_never_use_confusing_letters():
    assert "I" not in CODE_LETTERS and "O" not in CODE_LETTERS


def test_create_never_reuses_a_code(monkeypatch):
    manager = RoomManager()
    first, _ = manager.create("Ate")
    codes = iter([first.code, first.code, "ZZZZ"])  # two clashes, then a free code
    monkeypatch.setattr(random, "choices", lambda *a, **k: list(next(codes)))
    second, _ = manager.create("Kuya")
    assert second.code == "ZZZZ"
    assert len(manager.rooms) == 2


def test_join_is_case_and_space_insensitive_and_makes_a_holder():
    manager = RoomManager()
    room, _ = manager.create("Mama")
    joined_room, partner = manager.join(f"  {room.code.lower()} ", "Bunso")
    assert joined_room is room
    assert partner.role == HOLDER
    assert room.ready


def test_unknown_code_is_rejected():
    with pytest.raises(ValueError, match="No room"):
        RoomManager().join("ZZZZ", "Nobody")


def test_third_player_is_rejected_and_not_added():
    manager, room, _, _ = make_full_room()
    with pytest.raises(ValueError, match="full"):
        manager.join(room.code, "Third")
    assert len(room.players) == 2


def test_blank_name_becomes_player():
    _, player = RoomManager().create("   ")
    assert player.name == "Player"


def test_player_ids_are_unique_and_looked_up():
    _, room, host, partner = make_full_room()
    assert host.id != partner.id
    assert room.player(host.id) is host
    assert room.player(partner.id) is partner
    assert room.player("nope") is None


def test_partner_of():
    _, room, host, partner = make_full_room()
    assert room.partner_of(host) is partner
    assert room.partner_of(partner) is host


def test_partner_of_is_none_when_alone():
    room, host = RoomManager().create("Mama")
    assert room.partner_of(host) is None


def test_rooms_are_independent():
    manager = RoomManager()
    room1, _ = manager.create("Ate")
    room2, _ = manager.create("Kuya")
    assert room1 is not room2
    assert room1.game is not room2.game
    assert len(room1.players) == len(room2.players) == 1


def test_new_round_swaps_roles_and_makes_a_fresh_game():
    _, room, host, partner = make_full_room()
    old_game = room.game
    room.game.start()
    room.new_round()
    assert (host.role, partner.role) == (HOLDER, GUESSER)
    assert room.game is not old_game
    assert room.game.state == WAITING

    room.new_round()
    assert (host.role, partner.role) == (GUESSER, HOLDER)


def test_a_new_room_has_a_five_word_board_ready():
    room = Room("ABCD")
    assert len(room.game.board) == 5
    assert room.game.state == WAITING
