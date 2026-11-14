"""Smoke tests for what main.py sets up: the app starts and its pages are registered."""
from nicegui.testing import User


async def test_lobby_page_loads(user: User):
    await user.open("/")
    await user.should_see("Pinoy Genius")
    await user.should_see("Gumawa ng room")
    await user.should_see("Sumali sa room")


async def test_unknown_room_shows_a_friendly_message(user: User):
    await user.open("/room/ZZZZ/not-a-player")
    await user.should_see("Hindi nahanap ang room.")
    await user.should_see("Bumalik")
